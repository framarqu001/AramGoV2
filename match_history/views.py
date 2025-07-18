import time
import json

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
        match_data.append((match, main_participant, blue_team_list.copy(), red_team_list.copy(), main_stats))
    return match_data


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


def match_details(request, match_id):
    """
    View for displaying detailed match information.
    Includes expanded statistics and timeline data.
    Uses caching for expensive calculations.
    """
    # Try to get match details from cache first
    cache_key = f'match_details_{match_id}'
    match_data = cache.get(cache_key)
    
    if not match_data:
        # If not in cache, fetch and process the data
        try:
            match = get_object_or_404(Match, match_id=match_id)
            
            # Prefetch all participants with related data
            participants = Participant.objects.filter(match=match).select_related(
                'summoner', 'champion', 'spell1', 'spell2', 'rune1', 'rune2',
                'item1', 'item2', 'item3', 'item4', 'item5', 'item6'
            )
            
            # Separate participants by team
            blue_team = []
            red_team = []
            for participant in participants:
                if participant.team == Match.BLUE_TEAM:
                    blue_team.append(participant)
                else:
                    red_team.append(participant)
            
            # Process timeline data
            timeline_data = None
            if match.timeline_data:
                timeline_data = _process_timeline_data(match)
            
            # Calculate team statistics
            team_stats = _calculate_team_stats(match, blue_team, red_team)
            
            # Create match data dictionary
            match_data = {
                'match': match,
                'blue_team': blue_team,
                'red_team': red_team,
                'timeline_data': timeline_data,
                'team_stats': team_stats
            }
            
            # Cache the data for 1 hour (3600 seconds)
            cache.set(cache_key, match_data, 3600)
        
        except Match.DoesNotExist:
            raise Http404("Match not found")
    
    # Render the template with match data
    return render(request, 'match_history/match_details.html', match_data)


def _process_timeline_data(match):
    """
    Process timeline data from the match.
    Returns structured data for display in the template.
    """
    # Get timeline data from cache or process it
    cache_key = f'timeline_data_{match.match_id}'
    processed_data = cache.get(cache_key)
    
    if not processed_data:
        try:
            # Parse timeline data from JSON string
            timeline_data = match.get_timeline_data()
            
            # Process frames to create a structured timeline
            processed_data = {
                'item_purchases': defaultdict(list),
                'timestamps': []
            }
            
            # Extract timestamps and events
            for frame in timeline_data.get('frames', []):
                timestamp = frame['timestamp']
                processed_data['timestamps'].append(timestamp)
                
                for event in frame.get('events', []):
                    if event['type'] == 'ITEM_PURCHASED':
                        participant_id = event['participantId']
                        processed_data['item_purchases'][participant_id].append({
                            'timestamp': event['timestamp'],
                            'itemId': event['itemId']
                        })
            
            # Cache the processed data for 1 hour
            cache.set(cache_key, processed_data, 3600)
        
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            # Handle errors in timeline data processing
            print(f"Error processing timeline data: {e}")
            processed_data = None
    
    return processed_data


def _calculate_team_stats(match, blue_team, red_team):
    """
    Calculate and return team statistics.
    Uses cached values when available.
    """
    cache_key = f'team_stats_{match.match_id}'
    team_stats = cache.get(cache_key)
    
    if not team_stats:
        # Calculate team statistics
        blue_team_damage_share = {}
        red_team_damage_share = {}
        blue_team_gold_share = {}
        red_team_gold_share = {}
        
        # Calculate damage and gold share for each participant
        for participant in blue_team:
            blue_team_damage_share[participant.id] = participant.get_damage_share()
            blue_team_gold_share[participant.id] = participant.get_gold_share()
        
        for participant in red_team:
            red_team_damage_share[participant.id] = participant.get_damage_share()
            red_team_gold_share[participant.id] = participant.get_gold_share()
        
        # Create team stats dictionary
        team_stats = {
            'blue_team_gold': match.blue_team_gold,
            'red_team_gold': match.red_team_gold,
            'blue_team_kills': match.blue_team_kills,
            'red_team_kills': match.red_team_kills,
            'blue_team_damage': match.blue_team_damage_dealt,
            'red_team_damage': match.red_team_damage_dealt,
            'gold_difference': match.get_gold_difference(),
            'kill_difference': match.get_kill_difference(),
            'blue_team_damage_share': blue_team_damage_share,
            'red_team_damage_share': red_team_damage_share,
            'blue_team_gold_share': blue_team_gold_share,
            'red_team_gold_share': red_team_gold_share
        }
        
        # Cache the team stats for 1 hour
        cache.set(cache_key, team_stats, 3600)
    
    return team_stats
