import time

from django.core.cache import cache
from django.db.models import Prefetch
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from match_history.models import Participant, Match, AccountStats, SummonerChampionStats, ChampionStatsPatch
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from match_history.util.populate_data import SummonerManager
from riotwatcher import ApiError
from django.core.paginator import Paginator
from collections import defaultdict
from .tasks import *

patch = "14.17"


def home(request):
    return render(request, 'match_history/index.html')


def about(request):
    return render(request, "match_history/about.html")


def handlerException(request, exception=None):
    print(exception)
    message = ""
    strType = ''
    if isinstance(exception, Http404):
        message = "This Page Does Not Exist"
        strType = "404"
    elif isinstance(exception, HttpResponseBadRequest):
        message = "Bad Request"
        strType = "400"
    context = {
        'type': strType,
        'error': message
    }
    response = render(request, "match_history/exception.html", context)
    response.status_code = 404
    return response


@require_POST
def update(request):
    print("here")
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    summoner_id = request.POST.get('summoner_id')
    if not summoner_id:
        return JsonResponse({'error': 'Summoner ID is required'}, status=400)

    cache_key = f'update-cooldown-{session_key}-{summoner_id}'

    last_update_time = cache.get(cache_key)
    current_time = time.time()
    cooldown_duration = 600
    if last_update_time:
        time_since_last_update = current_time - last_update_time
        if time_since_last_update < cooldown_duration:
            remaining_cooldown = cooldown_duration - time_since_last_update
            return JsonResponse({
                'error': 'Cooldown active. Please wait.',
                'remaining_cooldown': int(remaining_cooldown)
            }, status=429)

    cache.set(cache_key, current_time, timeout=cooldown_duration)

    task = update_matches.delay(summoner_id)
    return JsonResponse({'task_id': task.id}, status=202)


def details(request, game_name: str, tag: str):
    print("hey there")
    print(request.GET)
    try:
        summoner = _validate_summoner(game_name, tag)
    except Http404 as e:
        raise Http404("This Page Does Not Exist")

    if summoner.being_parsed:
        context = {
            "task_id": summoner.task_id,
            "summoner": summoner
        }
        return render(request, 'match_history/details.html', context)

    matches_queryset = _get_match_queryset(summoner)
    if matches_queryset is None:
        raise Http404("This page does not exist.")
    matches_per_page = 10
    paginator = Paginator(matches_queryset, matches_per_page)
    page_number = request.GET.get('page', 1)  #defaults to 1
    page_obj = paginator.get_page(page_number)

    summoner_champion_stats = _get_champions_queryset(summoner)
    main_champ = summoner_champion_stats[0].champion

    if request.GET.get('section') == 'update' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        update_page(summoner)
    elif request.GET.get('section') == 'paginate' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if int(page_number) <= paginator.num_pages:
            context = {"matches": _get_match_data(summoner, page_obj)}
            return render(request, 'match_history/match_list.html', context)
        else:
            return HttpResponse(status=204)

    context = {
        "summoner": summoner,
        "matches": _get_match_data(summoner, page_obj),
        "account_stats": _get_account_stats(summoner),
        "champion_stats": _get_champion_stats_data(summoner, summoner_champion_stats),
        "recent_list": _get_recent(summoner),
        "main_champ": main_champ,
    }

    return render(request, 'match_history/details.html', context)



def summoner(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("match_history:home"))

    try:
        full_name = request.POST.get('full_name')
        full_name = full_name.replace(" ", "").lower()
        summoner_name, tag = full_name.split("#")
    except ValueError:
        raise Http404("This Page Does Not Exist")

    try:
        print(f"Trying to retrieve {full_name} from db")
        Summoner.objects.get(normalized_game_name=summoner_name, normalized_tag_line=tag)
    except Summoner.DoesNotExist:
        print(f"Summoner not found, trying Riot servers for {full_name}")
        try:
            summonerBuilder = SummonerManager("americas", "na1")
            newSummoner = summonerBuilder.create_summoner(summoner_name, tag)
            task = process_matches.delay(newSummoner.puuid)
            newSummoner.task_id = task.task_id
            newSummoner.save()
        except ApiError as e:
            print(f"{full_name}  ot found in db or Riot servers")
            raise Http404("This Page Does Not Exist")
    return HttpResponseRedirect(reverse("match_history:details", args=[summoner_name, tag]))


def champions(request):
    champion_query = ChampionStatsPatch.objects.filter(patch__iexact=patch).prefetch_related('champion')
    champion_data = []

    for champion_stat in champion_query:
        champion_stat_tuple = (
            champion_stat.patch,
            champion_stat.total_played,
            champion_stat.total_wins,
            champion_stat.total_losses,
        )
        champion_data.append((champion_stat.champion.name, champion_stat_tuple))
    context = {'champion_query': champion_data}
    return render(request, 'match_history/champions.html', context)


# ----------------------------------------------------------------------------------------------------------------------
def update_page(summoner):
    data = {
        'account_summary': render_to_string('match_history/account_summary.html',
                                            {'account_stats': _get_account_stats(summoner)}),
        'snowballs': render_to_string('match_history/snowballs.html', {'account_stats': _get_account_stats(summoner)}),
        'champion_list': render_to_string('match_history/champ_list.html',
                                          {'champion_stats': _get_champion_stats_data(summoner,
                                                                                      _get_champions_queryset(summoner))}),
        'recent_list': render_to_string('match_history/recent_list.html',
                                        {'recent_list': _get_recent(summoner)}),
        'match_list': render_to_string('match_history/match_list.html', {'matches': _get_new_match_data(summoner)})
    }
    return JsonResponse(data)

def _validate_summoner(game_name, tag):
    game_name, tag = game_name.replace(" ", "").lower(), tag.lower().replace(" ", "").lower()
    try:
        summoner = get_object_or_404(Summoner, normalized_game_name=game_name, normalized_tag_line=tag)
    except Http404:
        try:
            summoner_manager = SummonerManager("americas", "na1")
            puuid = summoner_manager._get_puid(game_name, tag)
            Summoner.objects.update_or_create(
                game_name=game_name, tag_line=tag, defaults={'puuid': puuid}
            )
        except ApiError:
            raise Http404(f"Summoner with game name {game_name} and tag {tag} could not be found and API call failed.")
    return summoner


def _get_new_match_data(summoner):
    matches_queryset = Match.objects.filter(participants__summoner=summoner, new_match=True).prefetch_related(
        Prefetch('participants', queryset=Participant.objects.select_related(
            'summoner', 'champion', "spell1", "spell2", "rune1", "rune2", "item1", "item2", "item3",
            'item4', 'item5', 'item6', 'summoner__profile_icon'),
                 to_attr='all_participants')
    )
    match_data = []

    for match in matches_queryset:
        blue_team_list = []
        red_team_list = []
        for participant in match.all_participants:
            if participant.summoner == summoner:
                main_participant = participant
            if participant.team == 100:
                blue_team_list.append(participant)
            else:
                red_team_list.append(participant)

        kda = (
                      main_participant.kills + main_participant.assists) / main_participant.deaths if main_participant.deaths else 0
        cs_min = main_participant.creep_score / (match.game_duration / 60) if match.game_duration > 0 else 0

        main_stats = {
            "kda": f"{kda:.2f}",
            "cs_min": f"{cs_min:.1f}"
        }
        match_data.append((match, main_participant, blue_team_list.copy(), red_team_list.copy(), main_stats))
    matches_queryset.update(new_match=False)
    return match_data


def _get_match_data(summoner, page_obj):
    match_data = []

    for match in page_obj:
        blue_team_list = []
        red_team_list = []
        for participant in match.all_participants:
            if participant.summoner == summoner:
                main_participant = participant
            if participant.team == 100:
                blue_team_list.append(participant)
            else:
                red_team_list.append(participant)

        kda = (
                      main_participant.kills + main_participant.assists) / main_participant.deaths if main_participant.deaths else 0
        cs_min = main_participant.creep_score / (match.game_duration / 60) if match.game_duration > 0 else 0

        main_stats = {
            "kda": f"{kda:.2f}",
            "cs_min": f"{cs_min:.1f}"
        }
        
        # Generate team composition analysis
        blue_team_comp = analyze_team_composition(blue_team_list)
        red_team_comp = analyze_team_composition(red_team_list)
        
        match_data.append((match, main_participant, blue_team_list.copy(), red_team_list.copy(), main_stats, blue_team_comp, red_team_comp))
    return match_data

def analyze_team_composition(team_list):
    """
    Analyze team composition to determine damage distribution and champion synergies.
    
    Args:
        team_list: List of participant objects representing a team
        
    Returns:
        Dictionary containing team composition analysis
    """
    # Initialize damage distribution counters
    ap_damage = 0
    ad_damage = 0
    true_damage = 0
    
    # Champion data for analysis
    champions = []
    champion_types = {}
    
    # Define champion damage types (simplified for demonstration)
    # In a real implementation, this would come from a database or API
    damage_types = {
        # Mages and AP champions
        'Ahri': 'ap', 'Annie': 'ap', 'Anivia': 'ap', 'Aurelion Sol': 'ap', 'Azir': 'ap',
        'Brand': 'ap', 'Cassiopeia': 'ap', 'Fiddlesticks': 'ap', 'Heimerdinger': 'ap',
        'Karma': 'ap', 'Karthus': 'ap', 'Kassadin': 'ap', 'Katarina': 'ap', 'Kennen': 'ap',
        'LeBlanc': 'ap', 'Lissandra': 'ap', 'Lux': 'ap', 'Malzahar': 'ap', 'Morgana': 'ap',
        'Neeko': 'ap', 'Orianna': 'ap', 'Ryze': 'ap', 'Seraphine': 'ap', 'Swain': 'ap',
        'Syndra': 'ap', 'Taliyah': 'ap', 'Twisted Fate': 'ap', 'Veigar': 'ap', 'Vel\'Koz': 'ap',
        'Viktor': 'ap', 'Vladimir': 'ap', 'Xerath': 'ap', 'Ziggs': 'ap', 'Zoe': 'ap', 'Zyra': 'ap',
        'Lillia': 'ap', 'Sylas': 'ap', 'Vex': 'ap', 'Akali': 'ap', 'Diana': 'ap', 'Ekko': 'ap',
        'Elise': 'ap', 'Evelynn': 'ap', 'Fizz': 'ap', 'Gragas': 'ap', 'Nidalee': 'ap',
        'Rumble': 'ap', 'Shyvana': 'ap', 'Teemo': 'ap',
        
        # AD champions
        'Ashe': 'ad', 'Caitlyn': 'ad', 'Corki': 'ad', 'Draven': 'ad', 'Ezreal': 'ad',
        'Graves': 'ad', 'Jhin': 'ad', 'Jinx': 'ad', 'Kai\'Sa': 'ad', 'Kalista': 'ad',
        'Kindred': 'ad', 'Kog\'Maw': 'ad', 'Lucian': 'ad', 'Miss Fortune': 'ad', 'Samira': 'ad',
        'Senna': 'ad', 'Sivir': 'ad', 'Tristana': 'ad', 'Twitch': 'ad', 'Varus': 'ad',
        'Vayne': 'ad', 'Xayah': 'ad', 'Aphelios': 'ad', 'Zeri': 'ad',
        'Aatrox': 'ad', 'Camille': 'ad', 'Darius': 'ad', 'Fiora': 'ad', 'Gangplank': 'ad',
        'Garen': 'ad', 'Gnar': 'ad', 'Hecarim': 'ad', 'Illaoi': 'ad', 'Irelia': 'ad',
        'Jarvan IV': 'ad', 'Jax': 'ad', 'Jayce': 'ad', 'Kayn': 'ad', 'Kha\'Zix': 'ad',
        'Kled': 'ad', 'Lee Sin': 'ad', 'Master Yi': 'ad', 'Nocturne': 'ad', 'Olaf': 'ad',
        'Pantheon': 'ad', 'Pyke': 'ad', 'Qiyana': 'ad', 'Renekton': 'ad', 'Rengar': 'ad',
        'Riven': 'ad', 'Sett': 'ad', 'Shaco': 'ad', 'Talon': 'ad', 'Tryndamere': 'ad',
        'Urgot': 'ad', 'Vi': 'ad', 'Viego': 'ad', 'Wukong': 'ad', 'Xin Zhao': 'ad',
        'Yasuo': 'ad', 'Yone': 'ad', 'Zed': 'ad',
        
        # Mixed damage or true damage champions
        'Cho\'Gath': 'true', 'Darius': 'true', 'Fiora': 'true', 'Garen': 'true',
        'Master Yi': 'true', 'Olaf': 'true', 'Pyke': 'true', 'Sett': 'true',
        'Vayne': 'true', 'Vel\'Koz': 'true', 'Camille': 'true',
    }
    
    # Define champion synergies (simplified for demonstration)
    synergies = {
        ('Yasuo', 'Yone'): 'Brother synergy',
        ('Caitlyn', 'Vi'): 'Piltover synergy',
        ('Garen', 'Lux'): 'Demacian synergy',
        ('Katarina', 'Garen'): 'Romantic synergy',
        ('Xayah', 'Rakan'): 'Lover synergy',
        ('Lucian', 'Senna'): 'Spouse synergy',
        ('Ashe', 'Tryndamere'): 'Freljord synergy',
        ('Leona', 'Diana'): 'Sun and Moon synergy',
    }
    
    # Analyze each champion in the team
    for participant in team_list:
        champion_name = participant.champion.name
        champion_types[champion_name] = damage_types.get(champion_name, 'ad')  # Default to AD if not found
        
        # Count damage types
        if champion_types[champion_name] == 'ap':
            ap_damage += 1
        elif champion_types[champion_name] == 'ad':
            ad_damage += 1
        else:
            true_damage += 1
        
        # Check for synergies
        has_synergy = False
        synergy_description = ""
        for synergy_pair, description in synergies.items():
            if champion_name in synergy_pair:
                for other_participant in team_list:
                    other_champion = other_participant.champion.name
                    if other_champion != champion_name and other_champion in synergy_pair:
                        has_synergy = True
                        synergy_description = description
                        break
        
        # Add champion data
        champions.append({
            'name': champion_name,
            'icon_url': participant.champion.get_url,
            'has_synergy': has_synergy,
            'synergy_description': synergy_description
        })
    
    # Calculate damage distribution percentages
    total_champions = len(team_list)
    ap_percentage = int((ap_damage / total_champions) * 100) if total_champions > 0 else 0
    ad_percentage = int((ad_damage / total_champions) * 100) if total_champions > 0 else 0
    true_percentage = int((true_damage / total_champions) * 100) if total_champions > 0 else 0
    
    # Adjust percentages to ensure they sum to 100%
    adjustment = 100 - (ap_percentage + ad_percentage + true_percentage)
    if adjustment != 0:
        if ap_percentage > 0:
            ap_percentage += adjustment
        elif ad_percentage > 0:
            ad_percentage += adjustment
        elif true_percentage > 0:
            true_percentage += adjustment
    
    return {
        'champions': champions,
        'damage_distribution': {
            'ap': ap_percentage,
            'ad': ad_percentage,
            'true': true_percentage
        }
    }


def _get_recent(summoner):
    matches_queryset = _get_match_queryset(summoner)
    counter = defaultdict(lambda: {'count': 0, 'wins': 0})
    matches = matches_queryset[:50]
    games_played = len(matches)
    main_team = None
    for match in matches:
        for participant in match.all_participants:
            if participant.summoner == summoner:
                main_team = participant.team
                break;

        for participant in match.all_participants:
            if participant.team != main_team or participant.summoner == summoner:
                continue
            if participant.win:
                counter[participant.summoner]['wins'] += 1
            counter[participant.summoner]['count'] += 1
    recent_sorted = sorted(counter.items(), key=lambda item: item[1]['count'], reverse=True)[:7]

    recent_stats = []
    for participant in recent_sorted:
        total_played = participant[1]['count']
        if total_played == 1:
            continue
        total_wins = participant[1]['wins']
        total_loses = total_played - total_wins
        win_rate = (total_wins / total_played * 100) if total_played > 0 else 0
        stats = {
            'participant': participant[0],
            'total_wins': participant[1]['wins'],
            'total_losses': total_loses,
            'winrate': int(round(win_rate)),
        }
        recent_stats.append(stats)
    return games_played, recent_stats


def _get_champion_stats_data(summoner, summoner_champion_stats):
    if not summoner_champion_stats:
        return
    champion_stats_data = []
    for stat in summoner_champion_stats:
        win_rate = (stat.total_wins / stat.total_played * 100) if stat.total_played > 0 else 0
        average_kills = stat.total_kills / stat.total_played
        average_deaths = stat.total_deaths / stat.total_played
        average_assists = stat.total_assists / stat.total_played
        kda = (average_kills + average_assists) / average_deaths if average_deaths else 0
        champion_data = {
            "total_played": stat.total_played,
            "total_wins": stat.total_wins,
            "total_losses": stat.total_losses,
            "winrate": int(round(win_rate)),
            "kills": f"{average_kills:.1f}".rstrip('0').rstrip('.'),
            "deaths": f"{average_deaths:.1f}".rstrip('0').rstrip('.'),
            "assists": f"{average_assists:.1f}".rstrip('0').rstrip('.'),
            "kda": f"{kda:.2f}".rstrip('0').rstrip('.'),
            "year": stat.year
        }
        champion_stats_data.append((stat.champion, champion_data))
    return champion_stats_data


def _get_account_stats(summoner):
    account_stats = AccountStats.objects.filter(summoner=summoner, year=2024).first()
    if not account_stats:
        return
    win_rate = (account_stats.total_wins / account_stats.total_played * 100) if account_stats.total_played > 0 else 0
    average_kills = account_stats.total_kills / account_stats.total_played
    average_deaths = account_stats.total_deaths / account_stats.total_played
    average_assists = account_stats.total_assists / account_stats.total_played
    kda = (average_kills + average_assists) / average_deaths if average_deaths else 0
    account_stats = {
        "total_played": account_stats.total_played,
        "total_wins": account_stats.total_wins,
        "total_losses": account_stats.total_losses,
        "winrate": int(round(win_rate)),
        "kills": f"{average_kills:.1f}".rstrip('0').rstrip('.'),
        "deaths": f"{average_deaths:.1f}".rstrip('0').rstrip('.'),
        "assists": f"{average_assists:.1f}".rstrip('0').rstrip('.'),
        "kda": f"{kda:.2f}".rstrip('0').rstrip('.'),
        "snowballs_hitrate": account_stats.get_snowball_percent(),
        'snowballs_thrown': account_stats.snowballs_thrown
    }
    return account_stats


def _get_match_queryset(summoner):
    matches_queryset = Match.objects.filter(participants__summoner=summoner).prefetch_related(
        Prefetch('participants', queryset=Participant.objects.select_related(
            'summoner', 'champion', "spell1", "spell2", "rune1", "rune2", "item1", "item2", "item3",
            'item4', 'item5', 'item6', 'summoner__profile_icon'),
                 to_attr='all_participants')
    )
    return matches_queryset


def _get_champions_queryset(summoner):
    summoner_champion_stats = SummonerChampionStats.objects.filter(summoner=summoner, year=2024).order_by(
        '-total_played')[:7].prefetch_related('champion')
    return summoner_champion_stats


def _get_main_champ(summoner):
    queryset = _get_champions_queryset(summoner)
    return queryset.first().champion
