import os
import django
from datetime import datetime as dt
import pytz
from riotwatcher import LolWatcher, RiotWatcher, ApiError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()
from match_history.models import *

RIOT_API_KEY = "RGAPI-00f5bc2b-4c2e-4c5b-8daf-4bf82d17e709"
QUEUE = 450  # Aram
COUNT = 20


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
                'summoner_name': info_dict["summoner_name"],
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

    def _create_match(self, match_id: str, match_info: dict):
        SECONDS = 60
        game_start = self._convert_stamp(match_info["gameStartTimestamp"])
        game_duration = match_info["gameDuration"] // SECONDS
        game_mode = match_info["gameMode"]
        game_version = match_info["gameVersion"]
        blue = match_info["teams"][0]["win"]
        winner = 100 if blue is True else 200

        match, created = Match.objects.update_or_create(
            match_id=match_id,
            defaults={
                "game_start": game_start,
                "game_duration": game_duration,
                "game_mode": game_mode,
                "game_version": game_version,
                "winner": winner
            }
        )
        if created:
            print(f"{match} created")
        else:
            print(f"{match} already exists")
        return match, created

    def _create_participants(self, match_info: dict, match: Match):
        participants_puid = match_info["metadata"]["participants"]

        summonermanager = SummonerManager()

        for i in range(len(participants_puid)):
            # Create a summoner for each participant in match
            participant_data = match_info["info"]["participants"][i]
            summoner_info = {"puuid": participants_puid[i], "game_name": participant_data.get("riotIdGameName", ""),
                             "tag": participant_data.get("riotIdTagline" ""),
                             "level": participant_data["summonerLevel"], "iconId": participant_data["profileIcon"],
                             "summoner_name": participant_data["summonerName"]}
            summoner: Summoner = summonermanager.create_summoner_match(summoner_info)
            # Create participant/stats for each participant in match

            ## Change this later, add a #id to champions
            champion: Champion = Champion.objects.get(champion_id__iexact=participant_data["championName"])

            kills = participant_data["kills"]
            deaths = participant_data["deaths"]
            assists = participant_data["assists"]
            creep_score = participant_data["totalMinionsKilled"]
            team_id = participant_data["teamId"]
            win = True if participant_data["win"] is True else False
            participant, created = Participant.objects.update_or_create(
                match=match,
                summoner=summoner,
                champion=champion,
                defaults={
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "creep_score": creep_score,
                    "team": team_id,
                    "win": win
                }
            )
            if created:
                print(f"{participant} added to match {match}")
            else:
                print(f"{participant} already exists ERORR!!!!")

            item_set = []
            for i in range(7):
                item_id = participant_data[f"item{i}"]
                print(item_id)
                if item_id != 0:
                    item = Item.objects.get(pk=participant_data[f"item{i}"])
                    item_set.append(item)
            participant.items.set(item_set)
            print("Added items")
        return

    def process_matches(self):
        count = 0
        for match in self._matches:
            if not Match.objects.filter(match_id=match).exists():
                match_info = self._get_match_info(match)
                match_model, created = self._create_match(match, match_info["info"])
                self._create_participants(match_info, match_model)
            else:
                print(f"{match} already exists")
            count += 1
            print(f"{count} matches processed")

    def _convert_stamp(self, unix_timestamp):
        unix_timestamp = unix_timestamp / 1000
        utc_datetime = dt.utcfromtimestamp(unix_timestamp)
        est_timezone = pytz.timezone('America/New_York')
        est_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(est_timezone)
        return est_datetime

    def set_summoner(self, summoner: Summoner):
        self._summoner = summoner
        self._matches = self._get_matches()


if __name__ == "__main__":
    summonerBuilder = SummonerManager("americas", "na1")
    summoner = summonerBuilder.create_summoner("MINTY", "017")
    matchBuilder = MatchManager("americas", "na1", summoner)
    matchBuilder.process_matches()
    summoners = Summoner.objects.all()
    for i in range(35):
        matchMaker = MatchManager("americas", "na1", summoners[i])
        matchMaker.process_matches()
        print("hey")
