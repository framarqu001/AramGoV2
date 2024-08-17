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


def details(request, game_name, tag):
    # Use get_object_or_404 to automatically handle cases where the summoner does not exist
    summoner_manager = SummonerManager("americas", "na1")
    try:
        puuid = summoner_manager._get_puid(game_name, tag)
    except ApiError:
        raise Http404

    summoner = get_object_or_404(Summoner, puuid=puuid)


    # Prefetch related participants, and their related champions and items to reduce query count
    matches = summoner.get_matches_queryset().prefetch_related(
        'participants',
        'participants__champion',
        'participants__items'
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
    summoner_name, tag = full_name.split("#")

    try:
        print(f"Trying to retrieve {full_name} from db")
        Summoner.objects.get(game_name=summoner_name, tag_line=tag)
    except Summoner.DoesNotExist:
        print(f"Summoner not found, trying Riot servers for {full_name}")
        summonerBuilder = SummonerManager("americas", "na1")

        try:
            # Create the summoner and ensure it is saved to the database
            newSummoner = summonerBuilder.create_summoner(summoner_name, tag)
            newSummoner.save()  # Ensure the summoner is saved
            print(f"Summoner {summoner_name} saved to database.")

            # Verify that the summoner exists in the database after saving
            if Summoner.objects.filter(game_name=summoner_name, tag_line=tag).exists():
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
