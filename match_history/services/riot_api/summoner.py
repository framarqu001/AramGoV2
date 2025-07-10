"""
Summoner API client for the Riot API service.
"""
import logging
from typing import Dict, Any, Optional

from match_history.models import Summoner, ProfileIcon
from match_history.services.riot_api.base import RiotAPIClient
from match_history.services.riot_api.exceptions import RiotAPINotFoundError

logger = logging.getLogger(__name__)


class SummonerAPIClient(RiotAPIClient):
    """
    Client for interacting with the Summoner endpoints of the Riot API.
    """
    
    def get_summoner_by_riot_id(self, game_name: str, tag_line: str) -> Dict[str, Any]:
        """
        Get a summoner by Riot ID (game name and tag line).
        
        Args:
            game_name (str): The summoner's game name.
            tag_line (str): The summoner's tag line.
            
        Returns:
            Dict[str, Any]: The summoner data.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            # First, get the PUUID from the account endpoint
            account_info = self.execute_with_retry(
                self.lol_watcher.account.by_riot_id,
                self.platform,
                game_name,
                tag_line
            )
            
            # Then, get the summoner details using the PUUID
            summoner_info = self.execute_with_retry(
                self.lol_watcher.summoner.by_puuid,
                self.region,
                account_info["puuid"]
            )
            
            # Combine the account and summoner information
            summoner_data = {
                **summoner_info,
                "gameName": account_info.get("gameName", ""),
                "tagLine": account_info.get("tagLine", ""),
            }
            
            return summoner_data
        
        except Exception as e:
            logger.error(f"Error getting summoner by Riot ID {game_name}#{tag_line}: {e}")
            raise
    
    def get_summoner_by_puuid(self, puuid: str) -> Dict[str, Any]:
        """
        Get a summoner by PUUID.
        
        Args:
            puuid (str): The summoner's PUUID.
            
        Returns:
            Dict[str, Any]: The summoner data.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            # Get the summoner details using the PUUID
            summoner_info = self.execute_with_retry(
                self.lol_watcher.summoner.by_puuid,
                self.region,
                puuid
            )
            
            # Try to get account info as well
            try:
                account_info = self.execute_with_retry(
                    self.lol_watcher.account.by_puuid,
                    self.platform,
                    puuid
                )
                
                # Combine the account and summoner information
                summoner_data = {
                    **summoner_info,
                    "gameName": account_info.get("gameName", ""),
                    "tagLine": account_info.get("tagLine", ""),
                }
            except Exception:
                # If account info can't be retrieved, just return summoner info
                summoner_data = summoner_info
            
            return summoner_data
        
        except Exception as e:
            logger.error(f"Error getting summoner by PUUID {puuid}: {e}")
            raise
    
    def get_summoner_by_name(self, summoner_name: str) -> Dict[str, Any]:
        """
        Get a summoner by summoner name.
        
        Args:
            summoner_name (str): The summoner's name.
            
        Returns:
            Dict[str, Any]: The summoner data.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            # Get the summoner details using the summoner name
            summoner_info = self.execute_with_retry(
                self.lol_watcher.summoner.by_name,
                self.region,
                summoner_name
            )
            
            # Try to get account info as well
            try:
                account_info = self.execute_with_retry(
                    self.lol_watcher.account.by_puuid,
                    self.platform,
                    summoner_info["puuid"]
                )
                
                # Combine the account and summoner information
                summoner_data = {
                    **summoner_info,
                    "gameName": account_info.get("gameName", ""),
                    "tagLine": account_info.get("tagLine", ""),
                }
            except Exception:
                # If account info can't be retrieved, just return summoner info
                summoner_data = summoner_info
            
            return summoner_data
        
        except Exception as e:
            logger.error(f"Error getting summoner by name {summoner_name}: {e}")
            raise
    
    def create_or_update_summoner(self, game_name: str, tag_line: str) -> Summoner:
        """
        Create or update a summoner in the database.
        
        Args:
            game_name (str): The summoner's game name.
            tag_line (str): The summoner's tag line.
            
        Returns:
            Summoner: The created or updated summoner.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the base client.
        """
        try:
            # Get the summoner data from the API
            summoner_data = self.get_summoner_by_riot_id(game_name, tag_line)
            
            # Get or create the profile icon
            icon_id = summoner_data["profileIconId"]
            try:
                icon = ProfileIcon.objects.get(profile_id=icon_id)
            except ProfileIcon.DoesNotExist:
                # If the profile icon doesn't exist, use a default or None
                icon = None
            
            # Create or update the summoner
            summoner, created = Summoner.objects.update_or_create(
                puuid=summoner_data["puuid"],
                defaults={
                    'game_name': summoner_data.get("gameName", ""),
                    'normalized_game_name': summoner_data.get("gameName", "").replace(" ", "").lower(),
                    'summoner_name': summoner_data.get("name", ""),
                    'tag_line': summoner_data.get("tagLine", ""),
                    'normalized_tag_line': summoner_data.get("tagLine", "").replace(" ", "").lower(),
                    'summoner_level': summoner_data.get("summonerLevel", 0),
                    'profile_icon': icon,
                }
            )
            
            return summoner
        
        except Exception as e:
            logger.error(f"Error creating or updating summoner {game_name}#{tag_line}: {e}")
            raise