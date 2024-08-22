from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from match_history.models import Summoner, Participant, Match
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

    context = {
        "summoner": summoner,
        "matches": matches,
        "total_pages": paginator.num_pages,
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
            kda = (
                          main_participant.kills + main_participant.assists) / main_participant.deaths if main_participant.deaths else 0
            cs_min = main_participant.creep_score / (match.game_duration / 60) if match.game_duration > 0 else 0

            main_stats = {
                "kda": f"{kda:.2f}",
                "cs_min": f"{cs_min:.1f}"
            }
            match_data.append((match, main_participant, blue_team_list, red_team_list, main_stats))
    return match_data
