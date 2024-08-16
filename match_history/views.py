from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from match_history.models import Summoner
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


# Create your views here.

def home(request):
    return render(request, 'match_history/index.html')


def details(request, game_name, tag):
    # Use get_object_or_404 to automatically handle cases where the summoner does not exist
    summoner = get_object_or_404(Summoner, game_name=game_name, tag_line=tag)

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


## Do error handling. redirect to home if not came from a post
## Get the user info if the summoner not in the db
def summoner(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    full_name = request.POST['full_name']
    summoner_name, tag = full_name.split("#")
    summoner = Summoner.objects.filter(game_name='highkeysavage', tag_line='na1')
    return HttpResponseRedirect(reverse("match_history:details", args=[summoner_name, tag]))


def about(request):
    pass


def champions(reques):
    pass
