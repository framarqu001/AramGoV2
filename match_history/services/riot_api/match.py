"""
Match API client for the Riot API service.
"""
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from django.db import transaction
from django.utils import timezone

from match_history.models import (
    Match, Summoner, Champion, SummonerSpell, Rune, Item, Participant,
    SummonerChampionStats, AccountStats, ChampionStatsPatch, ProfileIcon
)
from match_history.services.riot_api.base import RiotAPIClient
from match_history.services.riot_api.exceptions import RiotAPINotFoundError
from match_history.services.riot_api.summoner import SummonerAPIClient
from match_history.util.populate_data import _convert_stamp

logger = logging.getLogger(__name__)


class MatchAPIClient(RiotAPIClient):
    """
    Client for interacting with the Match endpoints of the Riot API.
    """
    
    # ARAM queue ID
    ARAM_QUEUE_ID = 450
    
    def get_match_list_by_puuid(
        self,
        puuid: str,
        queue: int = ARAM_QUEUE_ID,
        start: int = 0,
        count: int = 20,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[str]:
        """
        Get a list of match IDs for a summoner.
        
        Args:
            puuid (str): The summoner's PUUID.
            queue (int, optional): The queue ID to filter by. Defaults to ARAM_QUEUE_ID.
            start (int, optional): The start index for pagination. Defaults to 0.
            count (int, optional): The number of matches to retrieve. Defaults to 20.
            start_time (int, optional): The start time in epoch milliseconds. Defaults to None.
            end_time (int, optional): The end time in epoch milliseconds. Defaults to None.
            
        Returns:
            List[str]: A list of match IDs.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            params = {
                "queue": queue,
                "start": start,
                "count": count,
            }
            
            if start_time:
                params["startTime"] = start_time
            
            if end_time:
                params["endTime"] = end_time
            
            match_list = self.execute_with_retry(
                self.lol_watcher.match.matchlist_by_puuid,
                self.platform,
                puuid,
                **params
            )
            
            return match_list
        
        except Exception as e:
            logger.error(f"Error getting match list for PUUID {puuid}: {e}")
            raise
    
    def get_all_matches_by_puuid(
        self,
        puuid: str,
        queue: int = ARAM_QUEUE_ID,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        max_matches: int = 1000,
    ) -> List[str]:
        """
        Get all match IDs for a summoner, handling pagination.
        
        Args:
            puuid (str): The summoner's PUUID.
            queue (int, optional): The queue ID to filter by. Defaults to ARAM_QUEUE_ID.
            start_time (int, optional): The start time in epoch milliseconds. Defaults to None.
            end_time (int, optional): The end time in epoch milliseconds. Defaults to None.
            max_matches (int, optional): The maximum number of matches to retrieve. Defaults to 1000.
            
        Returns:
            List[str]: A list of match IDs.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            match_list = []
            start = 0
            count = 100  # Maximum allowed by the API
            
            while True:
                new_matches = self.get_match_list_by_puuid(
                    puuid,
                    queue=queue,
                    start=start,
                    count=count,
                    start_time=start_time,
                    end_time=end_time,
                )
                
                match_list.extend(new_matches)
                
                # Break if we've reached the end or the maximum number of matches
                if len(new_matches) < count or len(match_list) >= max_matches:
                    break
                
                start += count
            
            # Limit to max_matches
            return match_list[:max_matches]
        
        except Exception as e:
            logger.error(f"Error getting all matches for PUUID {puuid}: {e}")
            raise
    
    def get_match_by_id(self, match_id: str) -> Dict[str, Any]:
        """
        Get match details by match ID.
        
        Args:
            match_id (str): The match ID.
            
        Returns:
            Dict[str, Any]: The match details.
            
        Raises:
            RiotAPINotFoundError: If the match is not found.
            Other exceptions from the base client.
        """
        try:
            match_details = self.execute_with_retry(
                self.lol_watcher.match.by_id,
                self.platform,
                match_id
            )
            
            return match_details
        
        except Exception as e:
            logger.error(f"Error getting match details for match ID {match_id}: {e}")
            raise
    

