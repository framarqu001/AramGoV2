from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from match_history.models import Summoner, Participant, Match, AccountStats, SummonerChampionStats
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from populate_data import SummonerManager, MatchManager
from riotwatcher import ApiError
from django.db import transaction
from django.core.paginator import Paginator


# Create your views here.

def home(request):
    return render(request, 'match_history/index.html')


def details(request, game_name: str, tag: str):
    # Use get_object_or_404 to automatically handle cases where the summoner does not exist
    try:
        summoner = _validate_summoner(game_name, tag)
    except Http404 as e:
        raise Http404(e)

    matches_per_page = 5

    matches_queryset = Match.objects.filter(participants__summoner=summoner).prefetch_related(
        Prefetch('participants', queryset=Participant.objects.select_related(
            'summoner', 'champion', "spell1", "spell2", "rune1", "rune2", "item1", "item2", "item3",
            'item4', 'item5', 'item6'),
                 to_attr='all_participants')
    )

    paginator = Paginator(matches_queryset, matches_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    matches = _get_match_data(summoner, page_obj)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        context = {"matches": matches}
        return render(request, 'match_history/match_list.html', context)

    account_stats = AccountStats.objects.filter(summoner=summoner).first()
    champion_stats = SummonerChampionStats.objects.filter(summoner=summoner, year=2024).order_by('-total_played')[:7].prefetch_related(
        'champion'
    )
    champion_stats = _get_champion_stats_data(champion_stats)
    account_stats = _get_account_stats(account_stats)
    context = {
        "summoner": summoner,
        "matches": matches,
        "total_pages": paginator.num_pages,
        "account_stats": account_stats,
        "champion_stats": champion_stats,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'match_history/match_list.html', context)

    return render(request, 'match_history/details.html', context)


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
        summonerBuilder = SummonerManager("americas", "na1")

        try:
            # Create the summoner and ensure it is saved to the database
            newSummoner = summonerBuilder.create_summoner(summoner_name, tag)
            newSummoner.save()  # Ensure the summoner is saved
            print(f"Summoner {summoner_name} saved to database.")

            # Verify that the summoner exists in the database after saving
            if Summoner.objects.filter(normalized_game_name=summoner_name, normalized_tag_line=tag).exists():
                print(f"Confirmed: Summoner {summoner_name} exists in database.")
            else:
                print(f"ERROR: Summoner {summoner_name} not found in database after save.")
                raise Exception("Summoner save failed.")

            # Proceed with processing matches
            matchBuilder = MatchManager("americas", "na1", newSummoner)
            matchBuilder.process_matches()

        except ApiError as e:
            print(f"{full_name} not found in db or Riot servers")
            raise Http404

    return HttpResponseRedirect(reverse("match_history:details", args=[summoner_name, tag]))


def about(request):
    pass


def champions(reques):
    pass


def _validate_summoner(game_name, tag):
    game_name, tag = game_name.replace(" ", "").lower(), tag.lower().replace(" ", "").lower()
    try:
        summoner = get_object_or_404(Summoner, normalized_game_name=game_name, normalized_tag_line=tag)
    except Http404:
        try:
            summoner_manager = SummonerManager("americas", "na1")
            puuid = summoner_manager._get_puid(game_name, tag)
            # Assuming we might need to create or update the Summoner entry in our DB
            Summoner.objects.update_or_create(
                game_name=game_name, tag_line=tag, defaults={'puuid': puuid}
            )
        except ApiError:
            # If API call fails, raise Http404
            raise Http404(f"Summoner with game name {game_name} and tag {tag} could not be found and API call failed.")
    return summoner


def _get_match_data(summoner, page_obj):
    match_data = []
    for match in page_obj:
        main_participant_list = [p for p in match.all_participants if p.summoner == summoner]
        blue_team_list = [p for p in match.all_participants if p.team == 100]
        red_team_list = [p for p in match.all_participants if p.team == 200]

        main_participant = main_participant_list[0] if main_participant_list else None
        if main_participant:
            kda = (main_participant.kills + main_participant.assists) / main_participant.deaths if main_participant.deaths else 0
            cs_min = main_participant.creep_score / (match.game_duration / 60) if match.game_duration > 0 else 0

            main_stats = {
                "kda": f"{kda:.2f}",
                "cs_min": f"{cs_min:.1f}"
            }
            match_data.append((match, main_participant, blue_team_list, red_team_list, main_stats))
    return match_data

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