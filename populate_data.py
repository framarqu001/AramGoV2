import os

import django
from datetime import datetime as dt
import pytz
from riotwatcher import LolWatcher, RiotWatcher, ApiError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()

from match_history.models import *

RIOT_API_KEY = "RGAPI-24fe64cd-443a-41eb-a46a-b25faa1b3b98"
QUEUE = 450
COUNT = 100


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
            return account_info['puuid']
        except ApiError as err:
            print(f"Error fetching PUUID for {summoner_name}#{tag}: {err}")

    def _get_account_info(self, puid):
        try:
            # RiotWatcher provides the `by_puuid` method to get account information by PUUID
            account_info = self._lolWatcher.summoner.by_puuid(self._region, puid)
            return account_info
        except ApiError as err:
            print(f"Error fetching account info for PUUID {puid}: {err}")

    def create_summoner(self, summoner_name, tag):
        puuid = self._get_puid(summoner_name, tag)
        account_info = self._get_account_info(puuid)
        level = account_info["summonerLevel"]
        icon_id = account_info["profileIconId"]
        icon = ProfileIcon.objects.get(profile_id=icon_id)
        summoner, created = Summoner.objects.update_or_create(
            puuid=puuid,
            defaults={
                'game_name': summoner_name,
                'tag_line': tag,
                'summoner_level': level,
                'profile_icon': icon
            }
        )
        if created:
            print(f"{summoner} created")
        else:
            print(f"{summoner} already exists")
        return summoner

    def create_summoner_match(self, info_dict):
        icon_id = info_dict["iconId"]
        icon = ProfileIcon.objects.get(profile_id=icon_id)
        summoner, created = Summoner.objects.update_or_create(
            puuid=info_dict["puuid"],
            defaults={
                'game_name': info_dict["game_name"],
                'tag_line': info_dict["tag"],
                'summoner_level': info_dict["level"],
                'profile_icon': icon
            }
        )
        if created:
            print(f"{summoner} created")
        else:
            print(f"{summoner} already exists")
        return summoner


class MatchManager():
    def __init__(self, platform, region, summoner: Summoner):
        self._watcher = LolWatcher(RIOT_API_KEY)
        self._platform = platform
        self._region = region
        self._summoner = summoner
        self._matches = self._get_matches()

    def _get_matches(self):
        try:
            match_list = self._watcher.match.matchlist_by_puuid(self._region, self._summoner.puuid, queue=QUEUE,
                                                                count=COUNT)
            return match_list
        except ApiError as err:
            print(f"API Error: {err}")

    def _get_match_info(self, match_id):
        try:
            match_details = self._watcher.match.by_id(self._region, match_id)
            return match_details
        except ApiError as err:
            print(f"Error fetching match info for match ID {match_id}: {err}")

    def _create_match(self, match_id: str, match_info: dict) -> Match:
        SECONDS = 60
        game_start = self._convert_stamp(match_info["gameStartTimestamp"])
        game_duration = match_info["gameDuration"] // SECONDS
        game_mode = match_info["gameMode"]
        game_version = match_info["gameVersion"]
        match = Match(
            match_id=match_id,
            game_start=game_start,
            game_duration=game_duration,
            game_mode=game_mode,
            game_version=game_version
        )
        return match

    def _create_participants(self, match_id: str, match_info: dict, participant_list):
        participants_puid = match_info["metadata"]["participants"]

        summonerManager = SummonerManager()

        for i in range(len(participants_puid)):
            participant_data = match_info["info"]["participants"][i]
            summoner_info = {"puuid": participants_puid[i], "game_name": participant_data.get("riotIdGameName", ""),
                             "tag": participant_data.get("riotIdTagline" ""),
                             "level": participant_data["summonerLevel"], "iconId": participant_data["profileIcon"]}
            summonerManager.create_summoner_match(summoner_info)

    def process_matches(self):
        created_matches = []
        created_participants = []

        for i in range(len(self._matches)):
            match_info = self._get_match_info(self._matches[i])
            created_matches.append(self._create_match(self._matches[i], match_info["info"]))
            created_participants.append(self._create_participants(self._matches[i], match_info, created_participants))
            print(f"{i} matches created");

        Match.objects.bulk_create(created_matches, ignore_conflicts=True)
        print("Bulk insertion complete")

    def _convert_stamp(self, unix_timestamp):
        unix_timestamp = unix_timestamp / 1000
        utc_datetime = dt.utcfromtimestamp(unix_timestamp)
        est_timezone = pytz.timezone('America/New_York')
        est_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(est_timezone)
        return est_datetime


if __name__ == "__main__":
    summonerBuilder = SummonerManager("americas", "na1")
    summoner = summonerBuilder.create_summoner("highkeysavage", "na1")
    matchBuilder = MatchManager("americas", "na1", summoner)
    matchBuilder.process_matches()
