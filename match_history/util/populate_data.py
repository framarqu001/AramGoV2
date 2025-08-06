import os
import logging
from decimal import Decimal

import django
from datetime import datetime as dt
import pytz
from riotwatcher import LolWatcher, RiotWatcher, ApiError

from AramGoV2 import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()
from match_history.models import *

RIOT_API_KEY = settings.RIOT_API_KEY
QUEUE = 450  # Aram
COUNT = 100
from django.db import transaction

# Configure logging for API operations
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class SummonerManager():
    def __init__(self, platform=None, region=None):
        self._lolWatcher = LolWatcher(RIOT_API_KEY)
        self._riotWatcher = RiotWatcher(RIOT_API_KEY)
        self._platform = platform
        self._region = region
        self._base_url = f"https://{platform}.api.riotgames.com"

    def _get_puid(self, summoner_name, tag):
        try:
            account_info = self._riotWatcher.account.by_riot_id(self._platform, summoner_name, tag)
            return account_info
        except ApiError as err:
            raise ApiError(f"Error fetching PUUID for {summoner_name}#{tag}: {err}")

    def _get_account_info(self, puid):
        try:
            account_info = self._lolWatcher.summoner.by_puuid(self._region, puid)
            return account_info
        except ApiError as err:
            raise ApiError(f"Failed to fetch account info for PUUID {puid}: {err}")

    def create_summoner(self, summoner_name, tag):
        try:
            account_names = self._get_puid(summoner_name, tag)
            account_info = self._get_account_info(account_names["puuid"])
        except ApiError as err:
            raise ApiError(f"Error during summoner creation for {summoner_name}#{tag}: {err}") from err
        level = account_info["summonerLevel"]
        icon_id = account_info["profileIconId"]
        icon = ProfileIcon.objects.get(profile_id=icon_id)
        summoner, created = Summoner.objects.update_or_create(
            puuid=account_info["puuid"],
            defaults={
                'game_name': account_names["gameName"],
                'normalized_game_name': account_names["gameName"].replace(" ", "").lower(),
                'tag_line': account_names["tagLine"],
                'normalized_tag_line': account_names["tagLine"].replace(" ", "").lower(),
                'summoner_level': level,
                'profile_icon': icon,
                'being_parsed': True
            }
        )
        return summoner



def _convert_stamp(unix_timestamp):
    unix_timestamp = unix_timestamp / 1000
    utc_datetime = dt.utcfromtimestamp(unix_timestamp)
    pst_timezone = pytz.timezone('America/Los_Angeles')
    pst_datetime = utc_datetime.astimezone(pst_timezone)
    return pst_datetime



class MatchManager():
    def __init__(self, platform, region, summoner: Summoner):
        self._watcher = LolWatcher(RIOT_API_KEY)
        self._platform = platform
        self._region = region
        self._summoner = summoner
        self._matches = []
        self._processed_matches = 0

    def _get_all(self):
        try:
            match_list = []
            start = 0
            while True:
                new_matches = self._watcher.match.matchlist_by_puuid(self._region, self._summoner.puuid, queue=QUEUE,
                                                                     count=COUNT, start=start)
                match_list += new_matches
                if len(new_matches) != COUNT:
                    break
                start += COUNT
            return match_list
        except ApiError as err:
            logger.error(f"API Error fetching match list for summoner {self._summoner.puuid}: {err}")
            raise

    def _get_20(self):
        match_list = []
        try:
            start = 0
            new_matches = self._watcher.match.matchlist_by_puuid(self._region, self._summoner.puuid, queue=QUEUE,count=20, start=start)
            match_list += new_matches

            return match_list
        except ApiError as err:
            logger.error(f"API Error fetching recent matches for summoner {self._summoner.puuid}: {err}")
            raise

    def _get_match_info(self, match_id):
        try:
            match_details = self._watcher.match.by_id(self._region, match_id)
            return match_details
        except ApiError as err:
            logger.error(f"Error fetching match info for match ID {match_id}: {err}")
            raise
    
    def _get_match_timeline(self, match_id):
        """Fetch match timeline data from Riot API for detailed statistics"""
        try:
            timeline_data = self._watcher.match.timeline_by_match(self._region, match_id)
            logger.debug(f"Successfully fetched timeline data for match {match_id}")
            return timeline_data
        except ApiError as err:
            logger.warning(f"Error fetching timeline data for match ID {match_id}: {err}")
            # Timeline data is optional, so we return None instead of raising
            return None
        except Exception as err:
            logger.error(f"Unexpected error fetching timeline data for match ID {match_id}: {err}")
            return None
    
    def _extract_damage_stats_from_timeline(self, timeline_data, participant_id):
        """Extract damage statistics from timeline data for a specific participant"""
        if not timeline_data or 'info' not in timeline_data:
            logger.debug(f"No timeline data available for participant {participant_id}")
            return None, None, None
        
        try:
            # Timeline data contains frames with participant stats
            frames = timeline_data['info']['frames']
            if not frames:
                return None, None, None
            
            # Get the last frame which contains cumulative stats
            last_frame = frames[-1]
            if 'participantFrames' not in last_frame:
                return None, None, None
            
            participant_frame = last_frame['participantFrames'].get(str(participant_id))
            if not participant_frame:
                return None, None, None
            
            # Extract damage stats from the participant frame
            damage_stats = participant_frame.get('damageStats', {})
            total_damage_dealt = damage_stats.get('totalDamageDone', None)
            damage_to_champions = damage_stats.get('totalDamageDoneToChampions', None)
            damage_taken = damage_stats.get('totalDamageTaken', None)
            
            logger.debug(f"Extracted damage stats for participant {participant_id}: "
                        f"total={total_damage_dealt}, to_champs={damage_to_champions}, taken={damage_taken}")
            
            return total_damage_dealt, damage_to_champions, damage_taken
            
        except (KeyError, IndexError, TypeError) as err:
            logger.warning(f"Error extracting damage stats from timeline for participant {participant_id}: {err}")
            return None, None, None
    
    def _calculate_kda_ratio(self, kills, deaths, assists):
        """Calculate KDA ratio with proper handling of zero deaths"""
        try:
            return Decimal(str((kills + assists) / max(deaths, 1))).quantize(Decimal('0.01'))
        except (TypeError, ValueError) as err:
            logger.warning(f"Error calculating KDA ratio for K:{kills} D:{deaths} A:{assists}: {err}")
            return None

    def _create_match(self, match_id: str, match_info: dict, new=False):

        blue = match_info["teams"][0]["win"]
        winner = 100 if blue is True else 200

        match, created = Match.objects.update_or_create(
            match_id=match_id,
            defaults={
                "game_start": _convert_stamp(match_info["gameStartTimestamp"]),
                "game_duration": match_info["gameDuration"],
                "game_mode": match_info["gameMode"],
                "game_version": match_info["gameVersion"],
                "winner": winner,
                "new_match": new
            }
        )

        return match, created

    def create_summoner_match(self, info_dict, game_creation):
        icon_id = info_dict["profileIcon"]
        try:
            icon = ProfileIcon.objects.get(profile_id=icon_id)
        except ProfileIcon.DoesNotExist:

            icon = None
        summoner_exist = Summoner.objects.filter(puuid=info_dict["puuid"])
        if summoner_exist and summoner_exist[0].last_updated and game_creation < summoner_exist[0].last_updated:
            return summoner_exist[0]
        summoner, created = Summoner.objects.update_or_create(
            puuid=info_dict["puuid"],
            defaults={
                'game_name': info_dict.get("riotIdGameName", ""),
                'normalized_game_name': info_dict.get("riotIdGameName", "").replace(" ", "").lower(),
                'summoner_name': info_dict["summonerName"],
                'tag_line': info_dict.get("riotIdTagline" ""),
                'normalized_tag_line': info_dict.get("riotIdTagline" "").replace(" ", "").lower(),
                'summoner_level': info_dict["summonerLevel"],
                'profile_icon': icon,
                'last_updated': game_creation,
                'being_parsed': False
            }
        )
        return summoner

    def _add_items(self, participant, participant_data):
        for j in range(6):
            item_id = participant_data[f"item{j}"]
            if item_id != 0:
                try:
                    item = Item.objects.get(pk=participant_data[f"item{j}"])
                    setattr(participant, f"item{j}", item)
                    participant.save()
                except Item.DoesNotExist:
                    print('ok')

    def _increment_models(self, participant, match, snowballs):
        patch = match.get_patch()
        year = match.game_start.year
        if participant.game_name.lower() == 'highkeysavage':
            print(f"{participant.champion} on {match.game_start} year: {year} on site: {match.get_time_diff()}")

        summoner_champ_stats, createad = SummonerChampionStats.objects.update_or_create(
            summoner=participant.summoner,
            champion=participant.champion,
            year=year
        )
        summoner_champ_stats.update_stats(participant, match)

        account_stats, created = AccountStats.objects.update_or_create(
            summoner=participant.summoner,
            year=year
        )
        account_stats.update_stats(participant, snowballs)

        champ_stats_patch, created = ChampionStatsPatch.objects.update_or_create(
            champion=participant.champion,
            patch=patch
        )
        champ_stats_patch.update_stats(participant)

    def _create_participants(self, match_info: dict, match: Match):
        participants_puid = match_info["metadata"]["participants"]
        
        # Fetch timeline data for damage statistics (optional)
        timeline_data = self._get_match_timeline(match.match_id)
        if timeline_data:
            logger.info(f"Timeline data available for match {match.match_id}")
        else:
            logger.info(f"Timeline data not available for match {match.match_id}, proceeding without damage stats")

        for i in range(len(participants_puid)):
            participant_data = match_info["info"]["participants"][i]
            summoner: Summoner = self.create_summoner_match(participant_data, match.game_start)
            champion: Champion = Champion.objects.get(champion_id__iexact=participant_data["championName"])
            team_id = participant_data["teamId"]
            win = True if participant_data["win"] is True else False
            spell1 = SummonerSpell.objects.get(spell_id=participant_data["summoner1Id"])
            spell2 = SummonerSpell.objects.get(spell_id=participant_data["summoner2Id"])
            
            # Extract basic stats
            kills = participant_data["kills"]
            deaths = participant_data["deaths"]
            assists = participant_data["assists"]
            
            # Calculate KDA ratio
            kda_ratio = self._calculate_kda_ratio(kills, deaths, assists)
            
            # Extract damage statistics from timeline data if available
            participant_id = i + 1  # Riot API uses 1-based indexing for participants
            total_damage_dealt, damage_to_champions, damage_taken = None, None, None
            
            if timeline_data:
                total_damage_dealt, damage_to_champions, damage_taken = self._extract_damage_stats_from_timeline(
                    timeline_data, participant_id
                )
            
            # If timeline data is not available, try to get damage stats from match data
            if total_damage_dealt is None and 'totalDamageDealt' in participant_data:
                total_damage_dealt = participant_data.get('totalDamageDealt')
                damage_to_champions = participant_data.get('totalDamageDealtToChampions')
                damage_taken = participant_data.get('totalDamageTaken')
                logger.debug(f"Using damage stats from match data for participant {participant_id}")
            
            try:
                rune1 = Rune.objects.get(
                    rune_id=participant_data["perks"]["styles"][0]["selections"][0]["perk"])
            except Rune.DoesNotExist:
                rune1 = None
            try:
                rune2 = Rune.objects.get(rune_id=participant_data["perks"]["styles"][1]["style"])
            except Rune.DoesNotExist:
                rune2 = None

            participant, created = Participant.objects.update_or_create(
                match=match,
                summoner=summoner,
                champion=champion,
                defaults={
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "creep_score": participant_data["totalMinionsKilled"],
                    "team": team_id,
                    "win": win,
                    "game_name": participant_data.get("riotIdGameName", participant_data["summonerName"]),
                    "spell1": spell1,
                    "spell2": spell2,
                    "rune1": rune1,
                    "rune2": rune2,
                    # New extended statistics
                    "kda_ratio": kda_ratio,
                    "total_damage_dealt": total_damage_dealt,
                    "damage_to_champions": damage_to_champions,
                    "damage_taken": damage_taken,
                }
            )
            
            if created:
                logger.debug(f"Created new participant: {participant}")
            else:
                logger.debug(f"Updated existing participant: {participant}")
            
            total_snowballs = 0
            if participant.spell1.spell_id == 32:
                total_snowballs = participant_data["summoner1Casts"]
            elif participant.spell2.spell_id == 32:
                total_snowballs = participant_data["summoner2Casts"]
            snowball_hits = participant_data["challenges"]['snowballsHit']
            snowballs = (snowball_hits, total_snowballs)

            self._add_items(participant, participant_data)

            self._increment_models(participant, match, snowballs)

    def process_matches(self, progress_recorder=None):
        try:
            self._matches = self._get_all()
        except ApiError as err:
            logger.error(f"Failed to fetch match list for summoner {self._summoner.puuid}: {err}")
            return
        
        with transaction.atomic():
            total_matches = len(self._matches)
            self._summoner.being_parsed = True
            self._summoner.total_matches = total_matches
            self._summoner.save()
            logger.info(f"Starting to process {total_matches} matches for summoner {self._summoner.puuid}")

        for i, match in enumerate(self._matches):
            try:
                with transaction.atomic():
                    if not Match.objects.filter(match_id=match).exists():
                        try:
                            match_info = self._get_match_info(match)
                            match_model, created = self._create_match(match, match_info["info"])
                            self._create_participants(match_info, match_model)
                            if created:
                                logger.info(f"Successfully processed new match {match}")
                            else:
                                logger.debug(f"Updated existing match {match}")
                        except ApiError as api_err:
                            logger.error(f"API error processing match {match}: {api_err}")
                            continue  # Skip this match and continue with the next one
                        except Exception as err:
                            logger.error(f"Unexpected error processing match {match}: {err}")
                            continue  # Skip this match and continue with the next one

                    self._processed_matches += 1
                    self._summoner.parsed_matches += 1

                    if progress_recorder:
                        progress_recorder.set_progress(
                            self._summoner.parsed_matches,
                            self._summoner.total_matches,
                            description="matches processed")
                        self._summoner.save()
                        
            except Exception as err:
                logger.error(f"Critical error in match processing loop for match {match}: {err}")
                # Continue processing other matches even if one fails

        with transaction.atomic():
            self._summoner.being_parsed = False
            self._summoner.save()
            logger.info(f"Completed processing matches for summoner {self._summoner.puuid}. "
                       f"Processed {self._processed_matches} matches successfully.")

    def last_20(self, progress_recorder=None):
        try:
            self._matches = self._get_20()
        except ApiError as err:
            logger.error(f"Failed to fetch recent matches for summoner {self._summoner.puuid}: {err}")
            return
            
        total_matches = len(self._matches)
        logger.info(f"Processing {total_matches} recent matches for summoner {self._summoner.puuid}")

        for i, match in enumerate(self._matches):
            try:
                with transaction.atomic():
                    if not Match.objects.filter(match_id=match).exists():
                        try:
                            match_info = self._get_match_info(match)
                            match_model, created = self._create_match(match, match_info["info"], new=True)
                            self._create_participants(match_info, match_model)
                            logger.info(f"Successfully processed recent match {match}")
                        except ApiError as api_err:
                            logger.error(f"API error processing recent match {match}: {api_err}")
                            continue
                        except Exception as err:
                            logger.error(f"Unexpected error processing recent match {match}: {err}")
                            continue
                            
                    if progress_recorder:
                        progress_recorder.set_progress(i, total_matches, description="matches processed")
                        
            except Exception as err:
                logger.error(f"Critical error in recent match processing for match {match}: {err}")
                continue
                
        logger.info(f"Completed processing recent matches for summoner {self._summoner.puuid}")




if __name__ == "__main__":
    summonerBuilder = SummonerManager("americas", "na1")
    summonertest = summonerBuilder.create_summoner("kittykatmarco", 'na1')
    matchBuilder = MatchManager("americas", "na1", summonertest)
    matchBuilder.process_matches()
    summoners = Summoner.objects.all()
    for i in range(35):
        matchMaker = MatchManager("americas", "na1", summoners[i])
        matchMaker.process_matches()
