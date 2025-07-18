import os

from celery import shared_task

from match_history.util.populate_data import Summoner, MatchManager
from match_history.util.timeline_processor import process_match_timeline
from match_history.models import Match
from celery_progress.backend import ProgressRecorder


@shared_task(bind=True)
def process_matches(self, summoner_id):
    print('test')
    try:
        progress_recorder = ProgressRecorder(self)
        summoner = Summoner.objects.get(puuid=summoner_id)
        match_builder = MatchManager("americas", "na1", summoner)
        matches = match_builder.process_matches(progress_recorder=progress_recorder)
        
        # Process timeline data for new matches
        if matches:
            process_match_timelines.delay([match.match_id for match in matches])
    except Summoner.DoesNotExist:
        print(f"Summoner with id {summoner_id} does not exist")
    except Exception as e:
        print("Summoner could not be parsed")
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
        matches = match_builder.last_20(progress_recorder=progress_recorder)
        
        # Process timeline data for new matches
        if matches:
            process_match_timelines.delay([match.match_id for match in matches])
    except Summoner.DoesNotExist:
        print(f"Summoner with id {summoner_id} does not exist")


@shared_task
def process_match_timelines(match_ids):
    """
    Process timeline data for a list of matches
    
    Args:
        match_ids (list): List of match IDs to process
    """
    from riotwatcher import LolWatcher
    
    api_key = os.environ.get('RIOT_API_KEY')
    if not api_key:
        print("No Riot API key found")
        return
    
    watcher = LolWatcher(api_key)
    
    for match_id in match_ids:
        try:
            # Check if match exists and doesn't already have timeline data
            match = Match.objects.get(match_id=match_id)
            if not match.has_timeline:
                # Get timeline data from Riot API
                timeline_data = watcher.match.timeline_by_match('americas', match_id)
                
                # Process timeline data
                process_match_timeline(match_id, timeline_data)
        except Match.DoesNotExist:
            print(f"Match {match_id} does not exist")
        except Exception as e:
            print(f"Error processing timeline for match {match_id}: {e}")
