"""
Champion API client for the Riot API service.
"""
import logging
from typing import Dict, Any, List, Optional

from django.core.cache import cache

from match_history.models import Champion, ProfileIcon, Item, SummonerSpell, Rune
from match_history.services.riot_api.base import RiotAPIClient
from match_history.services.riot_api.exceptions import RiotAPINotFoundError

logger = logging.getLogger(__name__)


class ChampionAPIClient(RiotAPIClient):
    """
    Client for interacting with the Champion endpoints of the Riot API.
    """
    
    def get_champions(self) -> Dict[str, Any]:
        """
        Get all champions.
        
        Returns:
            Dict[str, Any]: The champions data.
            
        Raises:
            RiotAPINotFoundError: If the champions are not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["champion"]
            
            # Cache the patch version
            cache.set("PATCH", latest_version, timeout=24 * 60 * 60)  # 24 hours
            
            # Get all champions
            champions = self.execute_with_retry(
                self.lol_watcher.data_dragon.champions,
                latest_version
            )
            
            return champions
        
        except Exception as e:
            logger.error(f"Error getting champions: {e}")
            raise
    
    def get_items(self) -> Dict[str, Any]:
        """
        Get all items.
        
        Returns:
            Dict[str, Any]: The items data.
            
        Raises:
            RiotAPINotFoundError: If the items are not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["item"]
            
            # Get all items
            items = self.execute_with_retry(
                self.lol_watcher.data_dragon.items,
                latest_version
            )
            
            return items
        
        except Exception as e:
            logger.error(f"Error getting items: {e}")
            raise
    
    def get_summoner_spells(self) -> Dict[str, Any]:
        """
        Get all summoner spells.
        
        Returns:
            Dict[str, Any]: The summoner spells data.
            
        Raises:
            RiotAPINotFoundError: If the summoner spells are not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["summoner"]
            
            # Get all summoner spells
            spells = self.execute_with_retry(
                self.lol_watcher.data_dragon.summoner_spells,
                latest_version
            )
            
            return spells
        
        except Exception as e:
            logger.error(f"Error getting summoner spells: {e}")
            raise
    
    def get_profile_icons(self) -> Dict[str, Any]:
        """
        Get all profile icons.
        
        Returns:
            Dict[str, Any]: The profile icons data.
            
        Raises:
            RiotAPINotFoundError: If the profile icons are not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["profileicon"]
            
            # Get all profile icons
            icons = self.execute_with_retry(
                self.lol_watcher.data_dragon.profile_icons,
                latest_version
            )
            
            return icons
        
        except Exception as e:
            logger.error(f"Error getting profile icons: {e}")
            raise
    
    def get_runes(self) -> Dict[str, Any]:
        """
        Get all runes.
        
        Returns:
            Dict[str, Any]: The runes data.
            
        Raises:
            RiotAPINotFoundError: If the runes are not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["champion"]
            
            # Get all runes
            runes = self.execute_with_retry(
                self.lol_watcher.data_dragon.runes_reforged,
                latest_version
            )
            
            return runes
        
        except Exception as e:
            logger.error(f"Error getting runes: {e}")
            raise
    
    def update_static_data(self) -> None:
        """
        Update all static data (champions, items, summoner spells, profile icons, runes).
        
        Raises:
            RiotAPINotFoundError: If any of the data is not found.
            Other exceptions from the base client.
        """
        try:
            # Get the latest version
            versions = self.execute_with_retry(
                self.lol_watcher.data_dragon.versions_for_region,
                self.region
            )
            latest_version = versions["n"]["champion"]
            
            # Cache the patch version
            cache.set("PATCH", latest_version, timeout=24 * 60 * 60)  # 24 hours
            
            # Update champions
            champions_data = self.get_champions()
            for champion_id, champion_data in champions_data["data"].items():
                Champion.objects.update_or_create(
                    champion_id=champion_id,
                    defaults={
                        "name": champion_data["name"],
                        "title": champion_data["title"],
                        "image_path": champion_data["image"]["full"],
                        "splash_image_path": f"{champion_id}_0.jpg",
                    }
                )
            
            # Update items
            items_data = self.get_items()
            for item_id, item_data in items_data["data"].items():
                Item.objects.update_or_create(
                    item_id=item_id,
                    defaults={
                        "name": item_data["name"],
                        "image_path": item_data["image"]["full"],
                    }
                )
            
            # Update summoner spells
            spells_data = self.get_summoner_spells()
            for spell_id, spell_data in spells_data["data"].items():
                SummonerSpell.objects.update_or_create(
                    spell_id=spell_data["key"],
                    defaults={
                        "name": spell_data["name"],
                        "image_path": spell_data["image"]["full"],
                    }
                )
            
            # Update profile icons
            icons_data = self.get_profile_icons()
            for icon_id, icon_data in icons_data["data"].items():
                ProfileIcon.objects.update_or_create(
                    profile_id=icon_id,
                    defaults={
                        "image_path": icon_data["image"]["full"],
                    }
                )
            
            # Update runes
            runes_data = self.get_runes()
            for rune_category in runes_data:
                # Create the keystone runes
                for slot in rune_category["slots"]:
                    for rune in slot["runes"]:
                        Rune.objects.update_or_create(
                            rune_id=rune["id"],
                            defaults={
                                "name": rune["name"],
                                "image_path": rune["icon"],
                            }
                        )
        
        except Exception as e:
            logger.error(f"Error updating static data: {e}")
            raise