from celery import shared_task
from django.core.cache import cache

from populate_data import Summoner, MatchManager
from django.core.exceptions import ObjectDoesNotExist
from celery_progress.backend import ProgressRecorder


@shared_task(bind=True)
def process_matches(self, summoner_id):
    print('test')
    try:
        progress_recorder = ProgressRecorder(self)
        summoner = Summoner.objects.get(puuid=summoner_id)
        match_builder = MatchManager("americas", "na1", summoner)
        match_builder.process_matches(progress_recorder=progress_recorder)
    except Summoner.DoesNotExist:
        print(f"Summoner with id {summoner_id} does not exist")
    finally:
        summoner.being_parsed = False
        summoner.save()


@shared_task(bind=True)
def update_matches(self, summoner_id):
    print("task is being started")
    try:
        progress_recorder = ProgressRecorder(self)
        summoner = Summoner.objects.get(puuid=summoner_id)
        match_builder = MatchManager("americas", "na1", summoner)
        match_builder.last_20(progress_recorder=progress_recorder)
    except Summoner.DoesNotExist:
        print(f"Summoner with id {summoner_id} does not exist")
