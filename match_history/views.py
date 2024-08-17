from django.http import HttpResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import render, get_object_or_404
from match_history.models import Summoner
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from populate_data import SummonerManager, MatchManager
from riotwatcher import ApiError
from django.db import transaction


# Create your views here.

def home(request):
    return render(request, 'match_history/index.html')


def details(request, game_name: str, tag: str):
    # Use get_object_or_404 to automatically handle cases where the summoner does not exist
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

    matches = summoner.get_matches_queryset().prefetch_related(
        'participants',
        'participants__champion',
        'participants__items',
        'participants__summoner'
    )

    context = {
        "summoner": summoner,
        "matches": matches  # Pass matches to the context for use in the template
    }
    print(context)
    return render(request, 'match_history/details.html', context)



def summoner(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    full_name = request.POST.get('full_name')
    full_name = full_name.replace(" ", "").lower()
    summoner_name, tag = full_name.split("#")

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

        except ApiError as err:
            print(f"API Error: {err.message}")
            print(f"{full_name} not found in db or Riot servers")
            raise Http404

    return HttpResponseRedirect(reverse("match_history:details", args=[summoner_name, tag]))


def about(request):
    pass


def champions(reques):
    pass
