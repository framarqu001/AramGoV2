from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from match_history.models import Summoner, Participant, Match, AccountStats, SummonerChampionStats, ChampionStatsPatch
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from populate_data import SummonerManager, MatchManager
from riotwatcher import ApiError
from django.db import transaction
from django.core.paginator import Paginator
from collections import Counter, defaultdict
import pdb
from .tasks import *
from celery.result import AsyncResult


def home(request):
    return render(request, 'match_history/index.html')


@require_POST
def update(request):
    print("Hey there!")
    summoner_id = request.POST.get('summoner_id')
    task = update_matches.delay(summoner_id)  # Start the Celery task
    return JsonResponse({'task_id': task.id}, status=202)


def details(request, game_name: str, tag: str):
    # Use get_object_or_404 to automatically handle cases where the summoner does not exist
    try:
        summoner = _validate_summoner(game_name, tag)
    except Http404 as e:
        raise Http404(e)

    # if summoner.being_parsed:
    #     context = {
    #         "task_id": summoner.task_id,
    #         "summoner": summoner
    #     }
    #     return render(request, 'match_history/details.html', context)

    matches_per_page = 10

    matches_queryset = Match.objects.filter(participants__summoner=summoner).prefetch_related(
        Prefetch('participants', queryset=Participant.objects.select_related(
            'summoner', 'champion', "spell1", "spell2", "rune1", "rune2", "item1", "item2", "item3",
            'item4', 'item5', 'item6', 'summoner__profile_icon'),
                 to_attr='all_participants')
    )
    recent_list = _get_recent(summoner, matches_queryset)
    paginator = Paginator(matches_queryset, matches_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    matches = _get_match_data(summoner, page_obj)
    section = request.GET.get('section', None)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and section != "update":
        print('hi')
        if int(page_number) <= paginator.num_pages:
            context = {"matches": matches}
            return render(request, 'match_history/match_list.html', context)
        else:
            return HttpResponse(status=204)

    account_stats = AccountStats.objects.filter(summoner=summoner).first()
    champion_stats = SummonerChampionStats.objects.filter(summoner=summoner, year=2024).order_by('-total_played')[
                     :7].prefetch_related(
        'champion'
    )

    if account_stats:
        champion_stats = _get_champion_stats_data(champion_stats)
        account_stats = _get_account_stats(account_stats)

    print(section)
    if section == "update":
        print("hey")
        context = {
            'account_stats': account_stats,  # Fetch the latest account stats
            'champion_stats': champion_stats,  # Fetch the latest champions played stats
            'recent_stats': recent_list,  # Fetch the latest recently played stats
        }
        data = {
            'account_summary': render_to_string('match_history/account_summary.html', {'account_stats': context['account_stats']}),
            'champion_list': render_to_string('match_history/champ_list.html', {'champion_stats': context['champion_stats']}),
            'recent_list': render_to_string('match_history/recent_list.html', {'recent_list': context['recent_stats']}),
        }
        print(data['recent_list'])
        return JsonResponse(data)

    context = {
        "summoner": summoner,
        "matches": matches,
        "account_stats": account_stats,
        "champion_stats": champion_stats,
        "recent_list": recent_list,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'match_history/match_list.html', context)

    return render(request, 'match_history/details.html', context)


def load_account_summary(request, summoner_id):
    account_stats = AccountStats.objects.filter(summoner=summoner).first()
    champion_stats = SummonerChampionStats.objects.filter(summoner=summoner, year=2024).order_by('-total_played')[
                     :7].prefetch_related(
        'champion'
    )
    if account_stats:
        champion_stats = _get_champion_stats_data(champion_stats)
        account_stats = _get_account_stats(account_stats)
    context = {
        "account_stats": account_stats,
    }
    return render(request, 'match_history/account_summary.html', context)


def summoner(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        full_name = request.POST.get('full_name')
        full_name = full_name.replace(" ", "").lower()
        summoner_name, tag = full_name.split("#")
    except ValueError:
        return Http404("Invalid summoner name")

    try:
        print(f"Trying to retrieve {full_name} from db")
        Summoner.objects.get(normalized_game_name=summoner_name, normalized_tag_line=tag)
    except Summoner.DoesNotExist:
        print(f"Summoner not found, trying Riot servers for {full_name}")
        try:
            summonerBuilder = SummonerManager("americas", "na1")
            newSummoner = summonerBuilder.create_summoner(summoner_name, tag)
            # match_builder = MatchManager("americas", "na1", newSummoner)
            # match_builder.process_matches()
            # task = process_matches.delay(newSummoner.puuid)
            # newSummoner.being_parsed = True
            # newSummoner.task_id = task.task_id
            # newSummoner.save()

        except ApiError as e:
            print(f"{full_name} not found in db or Riot servers")
            raise Http404

    return HttpResponseRedirect(reverse("match_history:details", args=[summoner_name, tag]))


def about(request):
    pass


def champions(request):
    champion_query = ChampionStatsPatch.objects.filter(patch__iexact="14.16").prefetch_related('champion')
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
    print(match_data)
    return match_data


def _get_recent(summoner, matches_queryset):
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
            'winrate': f"{int(round(win_rate))}%",
        }
        recent_stats.append(stats)
    print(recent_stats)
    return games_played, recent_stats


def _get_champion_stats_data(summoner_champion_stats: SummonerChampionStats):
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
            "winrate": f"{int(round(win_rate))}%",
            "kills": f"{average_kills:.1f}".rstrip('0').rstrip('.'),
            "deaths": f"{average_deaths:.1f}".rstrip('0').rstrip('.'),
            "assists": f"{average_assists:.1f}".rstrip('0').rstrip('.'),
            "kda": f"{kda:.2f}".rstrip('0').rstrip('.'),
            "year": stat.year
        }
        champion_stats_data.append((stat.champion, champion_data))
    return champion_stats_data


def _get_account_stats(account_stats):
    win_rate = (account_stats.total_wins / account_stats.total_played * 100) if account_stats.total_played > 0 else 0
    average_kills = account_stats.total_kills / account_stats.total_played
    average_deaths = account_stats.total_deaths / account_stats.total_played
    average_assists = account_stats.total_assists / account_stats.total_played
    kda = (average_kills + average_assists) / average_deaths if average_deaths else 0
    account_stats = {
        "total_played": account_stats.total_played,
        "total_wins": account_stats.total_wins,
        "total_losses": account_stats.total_losses,
        "winrate": f"{int(round(win_rate))}%",
        "kills": f"{average_kills:.1f}".rstrip('0').rstrip('.'),
        "deaths": f"{average_deaths:.1f}".rstrip('0').rstrip('.'),
        "assists": f"{average_assists:.1f}".rstrip('0').rstrip('.'),
        "kda": f"{kda:.2f}".rstrip('0').rstrip('.'),
        "snowballs_hitrate": account_stats.get_snowball_percent(),
        'snowballs_thrown': account_stats.snowballs_thrown
    }
    return account_stats
