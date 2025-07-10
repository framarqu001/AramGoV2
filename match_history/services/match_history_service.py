"""
Match history service for processing and storing match data.
"""
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from django.db import transaction
from django.utils import timezone
from celery_progress.backend import ProgressRecorder

from match_history.models import (
    Match, Summoner, Champion, SummonerSpell, Rune, Item, Participant,
    SummonerChampionStats, AccountStats, ChampionStatsPatch, ProfileIcon
)
from match_history.services.riot_api.base import RiotAPIClient
from match_history.services.riot_api.exceptions import RiotAPIError, RiotAPINotFoundError
from match_history.services.riot_api.match import MatchAPIClient
from match_history.services.riot_api.summoner import SummonerAPIClient
from match_history.util.populate_data import _convert_stamp

logger = logging.getLogger(__name__)


class MatchHistoryService:
    """
    Service for processing and storing match history data.
    
    This service uses the Riot API clients to fetch match data and store it in the database.
    """
    
    def __init__(
        self,
        region: str = "na1",
        platform: str = "americas",
        use_cache: bool = True,
    ):
        """
        Initialize the match history service.
        
        Args:
            region (str, optional): The region to use for API requests. Defaults to "na1".
            platform (str, optional): The platform to use for API requests. Defaults to "americas".
            use_cache (bool, optional): Whether to use caching. Defaults to True.
        """
        self.region = region
        self.platform = platform
        self.use_cache = use_cache
        
        # Initialize API clients
        self.summoner_client = SummonerAPIClient(region=region, platform=platform, use_cache=use_cache)
        self.match_client = MatchAPIClient(region=region, platform=platform, use_cache=use_cache)
    
    def get_or_create_summoner(self, game_name: str, tag_line: str) -> Summoner:
        """
        Get or create a summoner by Riot ID.
        
        Args:
            game_name (str): The summoner's game name.
            tag_line (str): The summoner's tag line.
            
        Returns:
            Summoner: The summoner object.
            
        Raises:
            RiotAPINotFoundError: If the summoner is not found.
            Other exceptions from the API client.
        """
        try:
            return self.summoner_client.create_or_update_summoner(game_name, tag_line)
        except Exception as e:
            logger.error(f"Error getting or creating summoner {game_name}#{tag_line}: {e}")
            raise
    
    def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Get match details by match ID.
        
        Args:
            match_id (str): The match ID.
            
        Returns:
            Dict[str, Any]: The match details.
            
        Raises:
            RiotAPINotFoundError: If the match is not found.
            Other exceptions from the API client.
        """
        try:
            return self.match_client.get_match_by_id(match_id)
        except Exception as e:
            logger.error(f"Error getting match details for match ID {match_id}: {e}")
            raise
    
    def create_or_update_match(self, match_id: str, new_match: bool = False) -> Tuple[Match, bool]:
        """
        Create or update a match in the database.
        
        Args:
            match_id (str): The match ID.
            new_match (bool, optional): Whether this is a new match. Defaults to False.
            
        Returns:
            Tuple[Match, bool]: The match object and whether it was created.
            
        Raises:
            RiotAPINotFoundError: If the match is not found.
            Other exceptions from the API client.
        """
        try:
            # Get the match details from the API
            match_details = self.get_match_details(match_id)
            
            # Extract match info
            match_info = match_details["info"]
            
            # Determine the winner
            blue_team_win = match_info["teams"][0]["win"]
            winner = Match.BLUE_TEAM if blue_team_win else Match.RED_TEAM
            
            # Create or update the match
            match, created = Match.objects.update_or_create(
                match_id=match_id,
                defaults={
                    "game_start": _convert_stamp(match_info["gameStartTimestamp"]),
                    "game_duration": match_info["gameDuration"],
                    "game_mode": match_info["gameMode"],
                    "game_version": match_info["gameVersion"],
                    "winner": winner,
                    "new_match": new_match
                }
            )
            
            return match, created
        
        except Exception as e:
            logger.error(f"Error creating or updating match {match_id}: {e}")
            raise
    
    def create_or_update_participant_summoner(
        self,
        participant_data: Dict[str, Any],
        game_creation: Any
    ) -> Summoner:
        """
        Create or update a summoner from participant data.
        
        Args:
            participant_data (Dict[str, Any]): The participant data.
            game_creation: The game creation timestamp.
            
        Returns:
            Summoner: The created or updated summoner.
        """
        try:
            # Get or create the profile icon
            icon_id = participant_data["profileIcon"]
            try:
                icon = ProfileIcon.objects.get(profile_id=icon_id)
            except ProfileIcon.DoesNotExist:
                icon = None
            
            # Check if the summoner exists and if the game is older than the last update
            summoner_exist = Summoner.objects.filter(puuid=participant_data["puuid"])
            if summoner_exist and summoner_exist[0].last_updated and game_creation < summoner_exist[0].last_updated:
                return summoner_exist[0]
            
            # Create or update the summoner
            summoner, created = Summoner.objects.update_or_create(
                puuid=participant_data["puuid"],
                defaults={
                    'game_name': participant_data.get("riotIdGameName", ""),
                    'normalized_game_name': participant_data.get("riotIdGameName", "").replace(" ", "").lower(),
                    'summoner_name': participant_data["summonerName"],
                    'tag_line': participant_data.get("riotIdTagline", ""),
                    'normalized_tag_line': participant_data.get("riotIdTagline", "").replace(" ", "").lower(),
                    'summoner_level': participant_data["summonerLevel"],
                    'profile_icon': icon,
                    'last_updated': game_creation,
                    'being_parsed': False
                }
            )
            
            return summoner
        
        except Exception as e:
            logger.error(f"Error creating or updating participant summoner: {e}")
            raise
    
    def _add_items(self, participant: Participant, participant_data: Dict[str, Any]) -> None:
        """
        Add items to a participant.
        
        Args:
            participant (Participant): The participant object.
            participant_data (Dict[str, Any]): The participant data.
        """
        for j in range(6):
            item_id = participant_data[f"item{j}"]
            if item_id != 0:
                try:
                    item = Item.objects.get(pk=participant_data[f"item{j}"])
                    setattr(participant, f"item{j+1}", item)
                    participant.save()
                except Item.DoesNotExist:
                    logger.warning(f"Item with ID {item_id} not found")
    
    def _increment_models(
        self,
        participant: Participant,
        match: Match,
        snowballs: Tuple[int, int]
    ) -> None:
        """
        Increment statistics models for a participant.
        
        Args:
            participant (Participant): The participant object.
            match (Match): The match object.
            snowballs (Tuple[int, int]): Snowball hits and throws.
        """
        patch = match.get_patch()
        year = match.game_start.year
        
        # Update summoner champion stats
        summoner_champ_stats, created = SummonerChampionStats.objects.update_or_create(
            summoner=participant.summoner,
            champion=participant.champion,
            year=year
        )
        summoner_champ_stats.update_stats(participant, match)
        
        # Update account stats
        account_stats, created = AccountStats.objects.update_or_create(
            summoner=participant.summoner,
            year=year
        )
        account_stats.update_stats(participant, snowballs)
        
        # Update champion stats for the patch
        champ_stats_patch, created = ChampionStatsPatch.objects.update_or_create(
            champion=participant.champion,
            patch=patch
        )
        champ_stats_patch.update_stats(participant)
    
    def create_participants(self, match_details: Dict[str, Any], match: Match) -> None:
        """
        Create participants for a match.
        
        Args:
            match_details (Dict[str, Any]): The match details.
            match (Match): The match object.
        """
        participants_puids = match_details["metadata"]["participants"]
        
        for i in range(len(participants_puids)):
            participant_data = match_details["info"]["participants"][i]
            
            # Create or update the summoner
            summoner = self.create_or_update_participant_summoner(participant_data, match.game_start)
            
            # Get the champion
            try:
                champion = Champion.objects.get(champion_id__iexact=participant_data["championName"])
            except Champion.DoesNotExist:
                logger.error(f"Champion with name {participant_data['championName']} not found")
                continue
            
            # Get team and win status
            team_id = participant_data["teamId"]
            win = True if participant_data["win"] is True else False
            
            # Get summoner spells
            try:
                spell1 = SummonerSpell.objects.get(spell_id=participant_data["summoner1Id"])
                spell2 = SummonerSpell.objects.get(spell_id=participant_data["summoner2Id"])
            except SummonerSpell.DoesNotExist:
                logger.error(f"Summoner spell not found")
                continue
            
            # Get runes
            try:
                rune1 = Rune.objects.get(
                    rune_id=participant_data["perks"]["styles"][0]["selections"][0]["perk"]
                )
            except (Rune.DoesNotExist, KeyError, IndexError):
                rune1 = None
            
            try:
                rune2 = Rune.objects.get(
                    rune_id=participant_data["perks"]["styles"][1]["style"]
                )
            except (Rune.DoesNotExist, KeyError, IndexError):
                rune2 = None
            
            # Create or update the participant
            participant, created = Participant.objects.update_or_create(
                match=match,
                summoner=summoner,
                champion=champion,
                defaults={
                    "kills": participant_data["kills"],
                    "deaths": participant_data["deaths"],
                    "assists": participant_data["assists"],
                    "creep_score": participant_data["totalMinionsKilled"],
                    "team": team_id,
                    "win": win,
                    "game_name": participant_data.get("riotIdGameName", participant_data["summonerName"]),
                    "spell1": spell1,
                    "spell2": spell2,
                    "rune1": rune1,
                    "rune2": rune2,
                }
            )
            
            # Add items
            self._add_items(participant, participant_data)
            
            # Calculate snowball stats
            total_snowballs = 0
            if participant.spell1.spell_id == 32:
                total_snowballs = participant_data["summoner1Casts"]
            elif participant.spell2.spell_id == 32:
                total_snowballs = participant_data["summoner2Casts"]
            
            snowball_hits = participant_data["challenges"].get("snowballsHit", 0)
            snowballs = (snowball_hits, total_snowballs)
            
            # Update stats models
            self._increment_models(participant, match, snowballs)
    
    def process_match(self, match_id: str, new_match: bool = False) -> Match:
        """
        Process a match by ID.
        
        Args:
            match_id (str): The match ID.
            new_match (bool, optional): Whether this is a new match. Defaults to False.
            
        Returns:
            Match: The processed match.
        """
        try:
            # Get match details
            match_details = self.get_match_details(match_id)
            
            # Create or update the match
            match, created = self.create_or_update_match(match_id, new_match)
            
            # Create participants
            self.create_participants(match_details, match)
            
            return match
        
        except Exception as e:
            logger.error(f"Error processing match {match_id}: {e}")
            raise
    
    def process_matches(
        self,
        summoner: Summoner,
        progress_recorder: Optional[ProgressRecorder] = None
    ) -> None:
        """
        Process all matches for a summoner.
        
        Args:
            summoner (Summoner): The summoner object.
            progress_recorder (ProgressRecorder, optional): Progress recorder for Celery tasks.
                Defaults to None.
        """
        try:
            # Mark the summoner as being parsed
            with transaction.atomic():
                summoner.being_parsed = True
                summoner.save()
            
            # Get all match IDs
            match_ids = self.match_client.get_all_matches_by_puuid(summoner.puuid)
            
            # Set total matches
            with transaction.atomic():
                summoner.total_matches = len(match_ids)
                summoner.parsed_matches = 0
                summoner.save()
            
            # Process each match
            for i, match_id in enumerate(match_ids):
                with transaction.atomic():
                    # Skip if the match already exists
                    if not Match.objects.filter(match_id=match_id).exists():
                        self.process_match(match_id)
                    
                    # Update progress
                    summoner.parsed_matches += 1
                    
                    if progress_recorder:
                        progress_recorder.set_progress(
                            summoner.parsed_matches,
                            summoner.total_matches,
                            description="matches processed"
                        )
                    
                    summoner.save()
        
        except Exception as e:
            logger.error(f"Error processing matches for summoner {summoner}: {e}")
            raise
        
        finally:
            # Mark the summoner as not being parsed
            with transaction.atomic():
                summoner.being_parsed = False
                summoner.save()
    
    def process_recent_matches(
        self,
        summoner: Summoner,
        count: int = 20,
        progress_recorder: Optional[ProgressRecorder] = None
    ) -> None:
        """
        Process recent matches for a summoner.
        
        Args:
            summoner (Summoner): The summoner object.
            count (int, optional): Number of recent matches to process. Defaults to 20.
            progress_recorder (ProgressRecorder, optional): Progress recorder for Celery tasks.
                Defaults to None.
        """
        try:
            # Get recent match IDs
            match_ids = self.match_client.get_match_list_by_puuid(
                summoner.puuid,
                count=count
            )
            
            # Process each match
            for i, match_id in enumerate(match_ids):
                with transaction.atomic():
                    # Process the match as new if it doesn't exist
                    if not Match.objects.filter(match_id=match_id).exists():
                        self.process_match(match_id, new_match=True)
                    
                    # Update progress
                    if progress_recorder:
                        progress_recorder.set_progress(
                            i + 1,
                            len(match_ids),
                            description="matches processed"
                        )
        
        except Exception as e:
            logger.error(f"Error processing recent matches for summoner {summoner}: {e}")
            raise