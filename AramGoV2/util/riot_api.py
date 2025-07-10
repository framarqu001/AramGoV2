"""
Riot Games API Client Service

This module provides a centralized client for interacting with the Riot Games API.
It handles authentication, rate limiting, and error handling for API requests.
"""
import logging
import time
from typing import Dict, List, Optional, Any, Union

from django.conf import settings
from django.core.cache import cache
from riotwatcher import LolWatcher, RiotWatcher, ApiError

logger = logging.getLogger(__name__)

class RiotAPIClient:
    """
    A client for interacting with the Riot Games API.
    
    This class provides methods for fetching data from various Riot Games API endpoints,
    with built-in error handling, caching, and rate limit management.
    """
    
    # Constants for API regions and platforms
    REGIONS = {
        'na': 'na1',
        'euw': 'euw1',
        'eune': 'eun1',
        'kr': 'kr',
        'br': 'br1',
        'jp': 'jp1',
        'ru': 'ru',
        'oce': 'oc1',
        'tr': 'tr1',
        'lan': 'la1',
        'las': 'la2',
    }
    
    REGIONAL_ROUTES = {
        'na': 'americas',
        'br': 'americas',
        'lan': 'americas',
        'las': 'americas',
        'euw': 'europe',
        'eune': 'europe',
        'tr': 'europe',
        'ru': 'europe',
        'kr': 'asia',
        'jp': 'asia',
        'oce': 'sea',
    }
    
    # Queue types
    QUEUE_ARAM = 450
    
    def __init__(self, region: str = 'na'):
        """
        Initialize the Riot API client.
        
        Args:
            region: The region code (e.g., 'na', 'euw')
        """
        self.api_key = settings.RIOT_API_KEY
        if not self.api_key:
            logger.error("Riot API key not found in settings")
            raise ValueError("Riot API key is required but not provided in settings")
        
        self.region = region.lower()
        self.platform = self.REGIONS.get(self.region)
        self.regional_route = self.REGIONAL_ROUTES.get(self.region)
        
        if not self.platform or not self.regional_route:
            logger.error(f"Invalid region: {region}")
            raise ValueError(f"Invalid region: {region}")
        
        # Initialize API clients
        self.lol_watcher = LolWatcher(self.api_key)
        self.riot_watcher = RiotWatcher(self.api_key)
        
        logger.info(f"Initialized Riot API client for region {self.region}")
    
    def get_summoner_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        """
        Get summoner information by Riot ID (game name and tag line).
        
        Args:
            game_name: The summoner's game name
            tag_line: The summoner's tag line
            
        Returns:
            Dict containing summoner information
            
        Raises:
            ApiError: If the API request fails
        """
        cache_key = f"summoner:{game_name.lower()}:{tag_line.lower()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Cache hit for summoner {game_name}#{tag_line}")
            return cached_data
        
        try:
            # First get the PUUID from the account-v1 endpoint
            account_info = self.riot_watcher.account.by_riot_id(self.regional_route, game_name, tag_line)
            
            # Then get the full summoner info using the PUUID
            summoner_info = self.lol_watcher.summoner.by_puuid(self.platform, account_info["puuid"])
            
            # Combine the data
            result = {
                **summoner_info,
                "gameName": account_info.get("gameName"),
                "tagLine": account_info.get("tagLine"),
            }
            
            # Cache the result for 1 hour
            cache.set(cache_key, result, 3600)
            
            return result
        except ApiError as e:
            self._handle_api_error(e, f"Failed to get summoner by Riot ID: {game_name}#{tag_line}")
            raise
    
    def get_match_list(self, puuid: str, queue: int = QUEUE_ARAM, count: int = 20, start: int = 0) -> List[str]:
        """
        Get a list of match IDs for a summoner.
        
        Args:
            puuid: The summoner's PUUID
            queue: Queue type (default: ARAM)
            count: Number of matches to retrieve
            start: Starting index
            
        Returns:
            List of match IDs
            
        Raises:
            ApiError: If the API request fails
        """
        cache_key = f"matches:{puuid}:{queue}:{count}:{start}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Cache hit for match list of {puuid}")
            return cached_data
        
        try:
            match_list = self.lol_watcher.match.matchlist_by_puuid(
                self.regional_route, 
                puuid, 
                queue=queue,
                count=count, 
                start=start
            )
            
            # Cache the result for 5 minutes
            cache.set(cache_key, match_list, 300)
            
            return match_list
        except ApiError as e:
            self._handle_api_error(e, f"Failed to get match list for PUUID: {puuid}")
            raise
    
    def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a match.
        
        Args:
            match_id: The match ID
            
        Returns:
            Dict containing match details
            
        Raises:
            ApiError: If the API request fails
        """
        cache_key = f"match:{match_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Cache hit for match {match_id}")
            return cached_data
        
        try:
            match_details = self.lol_watcher.match.by_id(self.regional_route, match_id)
            
            # Cache the result for 1 day (match data doesn't change)
            cache.set(cache_key, match_details, 86400)
            
            return match_details
        except ApiError as e:
            self._handle_api_error(e, f"Failed to get match details for match ID: {match_id}")
            raise
    
    def get_all_matches(self, puuid: str, queue: int = QUEUE_ARAM) -> List[str]:
        """
        Get all available matches for a summoner.
        
        Args:
            puuid: The summoner's PUUID
            queue: Queue type (default: ARAM)
            
        Returns:
            List of all match IDs
            
        Raises:
            ApiError: If the API request fails
        """
        try:
            match_list = []
            start = 0
            count = 100  # Maximum allowed by the API
            
            while True:
                new_matches = self.get_match_list(puuid, queue, count, start)
                match_list.extend(new_matches)
                
                if len(new_matches) < count:
                    break
                    
                start += count
                # Add a small delay to avoid hitting rate limits
                time.sleep(1.2)
                
            return match_list
        except ApiError as e:
            self._handle_api_error(e, f"Failed to get all matches for PUUID: {puuid}")
            raise
    
    def _handle_api_error(self, error: ApiError, message: str) -> None:
        """
        Handle API errors with appropriate logging and responses.
        
        Args:
            error: The ApiError exception
            message: Context message for the error
        """
        status = error.response.status_code
        
        if status == 429:
            retry_after = error.response.headers.get('Retry-After', 5)
            logger.warning(f"Rate limit exceeded. Retry after {retry_after} seconds. {message}")
        elif status == 404:
            logger.info(f"Resource not found: {message}")
        elif status == 403:
            logger.error(f"API key invalid or expired: {message}")
        elif status >= 500:
            logger.error(f"Riot API server error ({status}): {message}")
        else:
            logger.error(f"API error ({status}): {message}")