import os
import django
from datetime import datetime as dt
import pytz
from riotwatcher import LolWatcher, RiotWatcher, ApiError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()
from match_history.models import *

RIOT_API_KEY = "RGAPI-694e1a5c-5426-4aa6-8f9a-8e9e3502fb47"
QUEUE = 450  # Aram
COUNT = 10


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
            raise ApiError(f"Error fetching PUUID for {summoner_name}#{tag}: {err}")

    def _get_account_info(self, puid):
        try:
            account_info = self._lolWatcher.summoner.by_puuid(self._region, puid)
            return account_info
        except ApiError as err:
            raise ApiError(f"Failed to fetch account info for PUUID {puid}: {err}")

    def create_summoner(self, summoner_name, tag):
        try:
            puuid = self._get_puid(summoner_name, tag)
            account_info = self._get_account_info(puuid)
        except ApiError as err:
            raise ApiError(f"Error during summoner creation for {summoner_name}#{tag}: {err}") from err
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

    def create_summoner_match(self, puuid):
        summoner, created = Summoner.objects.update_or_create(puuid=puuid)
        if created:
            print(f"{summoner} created")
        else:
            print(f"{summoner} already exists")
        return summoner

    def _create_participants(self, match_info: dict, match: Match):
        participants_puid = match_info["metadata"]["participants"]



        for i in range(len(participants_puid)):
            # Create a summoner for each participant in match
            participant_data = match_info["info"]["participants"][i]
            puuid = participants_puid[i]

            summoner: Summoner = self.create_summoner_match(puuid)
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
                    "win": win,
                    "game_name": participant_data.get("riotIdGameName", participant_data["summonerName"])
                }
            )
            if created:
                print(f"{participant} added to match {match}")
            else:
                print(f"{participant} already exists ERORR!!!!")

            item_set = []
            for i in range(7):
                item_id = participant_data[f"item{i}"]
                if item_id != 0:
                    item = Item.objects.get(pk=participant_data[f"item{i}"])
                    item_set.append(item)
            participant.items.set(item_set)
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
    summoner = summonerBuilder.create_summoner("Tabula Rasa", "adc")
    matchBuilder = MatchManager("americas", "na1", summoner)
    matchBuilder.process_matches()
    summoners = Summoner.objects.all()
    # for i in range(35):
    #     matchMaker = MatchManager("americas", "na1", summoners[i])
    #     matchMaker.process_matches()
    #     print("hey")
