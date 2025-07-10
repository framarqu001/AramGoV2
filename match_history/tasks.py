import logging

from celery import shared_task
from django.conf import settings

from match_history.models import Summoner
from match_history.services.match_history_service import MatchHistoryService
from match_history.services.riot_api.champion import ChampionAPIClient
from celery_progress.backend import ProgressRecorder

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_matches(self, summoner_id):
    """
    Process all matches for a summoner.
    
    Args:
        summoner_id (str): The summoner's PUUID.
    """
    logger.info(f"Processing matches for summoner {summoner_id}")
    try:
        progress_recorder = ProgressRecorder(self)
        summoner = Summoner.objects.get(puuid=summoner_id)
        
        # Create the match history service
        match_history_service = MatchHistoryService(
            region=settings.DEFAULT_REGION,
            platform=settings.DEFAULT_PLATFORM
        )
        
        # Process matches
        match_history_service.process_matches(
            summoner=summoner,
            progress_recorder=progress_recorder
        )
    except Summoner.DoesNotExist:
        logger.error(f"Summoner with id {summoner_id} does not exist")
    except Exception as e:
        logger.error(f"Error processing matches for summoner {summoner_id}: {e}")
    finally:
        # Ensure the summoner is marked as not being parsed
        try:
            summoner = Summoner.objects.get(puuid=summoner_id)
            summoner.being_parsed = False
            summoner.save()
        except Exception:
            pass


@shared_task(bind=True)
def update_matches(self, summoner_id):
    """
    Update recent matches for a summoner.
    
    Args:
        summoner_id (str): The summoner's PUUID.
    """
    logger.info(f"Updating matches for summoner {summoner_id}")
    try:
        progress_recorder = ProgressRecorder(self)
        summoner = Summoner.objects.get(puuid=summoner_id)
        
        # Create the match history service
        match_history_service = MatchHistoryService(
            region=settings.DEFAULT_REGION,
            platform=settings.DEFAULT_PLATFORM
        )
        
        # Process recent matches
        match_history_service.process_recent_matches(
            summoner=summoner,
            count=20,
            progress_recorder=progress_recorder
        )
    except Summoner.DoesNotExist:
        logger.error(f"Summoner with id {summoner_id} does not exist")
    except Exception as e:
        logger.error(f"Error updating matches for summoner {summoner_id}: {e}")


@shared_task
def update_static_data():
    """
    Update static data (champions, items, summoner spells, profile icons, runes).
    """
    logger.info("Updating static data")
    try:
        # Create the champion API client
        champion_client = ChampionAPIClient(
            region=settings.DEFAULT_REGION,
            platform=settings.DEFAULT_PLATFORM
        )
        
        # Update static data
        champion_client.update_static_data()
        
        logger.info("Static data updated successfully")
    except Exception as e:
        logger.error(f"Error updating static data: {e}")
