import os

import django
import requests
from datetime import datetime as dt
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()

from match_history.models import *

RIOT_API_KEY = "RGAPI-24fe64cd-443a-41eb-a46a-b25faa1b3b98"
QUEUE = 450
COUNT = 80


class SummonerManager():
    def __init__(self, platform, region):
        self._api_key = RIOT_API_KEY
        self._platform = platform
        self._region = region
        self._base_url = f"https://{platform}.api.riotgames.com"

    def _get_puid(self, summoner_name, tag):
        puid_url = f"/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}?api_key={self._api_key}"
        url = self._base_url + puid_url
        response = requests.get(url)
        response = response.json()
        return response["puuid"]

    def _get_account_info(self, puid):
        account_info_url = f"/lol/summoner/v4/summoners/by-puuid/{puid}?api_key={self._api_key}"
        temp_url = f"https://{self._region}.api.riotgames.com/"
        url = temp_url + account_info_url
        response = requests.get(url)
        response = response.json()
        return response

    def create_summoner(self, summoner_name, tag):
        puid = self._get_puid(summoner_name, tag)
        account_info = self._get_account_info(puid)
        level = account_info["summonerLevel"]
        icon_id = account_info["profileIconId"]
        icon = ProfileIcon.objects.get(profile_id=icon_id)
        summoner, created = Summoner.objects.update_or_create(
            defaults={
                'gameName': summoner_name,
                'tagLine': tag,
                'summoner_level': level,
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
        self._api_key = RIOT_API_KEY
        self._platform = platform
        self._region = region
        self._base_url = f"https://{platform}.api.riotgames.com"
        self._summoner = summoner
        self._matches = self._get_matches()

    def _get_matches(self):
        matches_url = f"/lol/match/v5/matches/by-puuid/{self._summoner.puid}/ids?queue={QUEUE}&start=0&count={COUNT}&api_key={self._api_key}"
        url = self._base_url + matches_url
        response = requests.get(url)
        response = response.json()
        return response

    def _get_match_info(self, match_id):
        match_info_url = f"/lol/match/v5/matches/{match_id}?api_key={self._api_key}"
        url = self._base_url + match_info_url
        response = requests.get(url)
        response = response.json()
        return response['info']

    def _create_match(self, match_id):
        match_info = self._get_match_info(match_id)
        game_start = self._convert_stamp(match_info["gameStartTimestamp"])
        game_duration = match_info["gameDuration"] // 60
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

    def process_matches(self):
        created_matches = []
        for i in range(len(self._matches)):
            created_matches.append(self._create_match(self._matches[i]))
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
