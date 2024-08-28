import os
from time import sleep

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
            print(account_info)
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
        if created:
            print(f"{summoner} created")
        else:
            print(f"{summoner} already exists")
        return summoner


def _convert_stamp(unix_timestamp):
    unix_timestamp = unix_timestamp / 1000
    utc_datetime = dt.utcfromtimestamp(unix_timestamp)
    est_timezone = pytz.timezone('America/New_York')
    est_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(est_timezone)
    return est_datetime


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
                print(f"Matches: {len(new_matches)}")
                if len(new_matches) != COUNT:
                    break
                start += COUNT
            return match_list
        except ApiError as err:
            print(f"API Error: {err}")

    def _get_20(self):
        match_list = []
        try:
            start = 0
            new_matches = self._watcher.match.matchlist_by_puuid(self._region, self._summoner.puuid, queue=QUEUE,count=20, start=start)
            match_list += new_matches

            return match_list
        except ApiError as err:
            print(f"API Error: {err}")

    def _get_match_info(self, match_id):
        try:
            match_details = self._watcher.match.by_id(self._region, match_id)
            return match_details
        except ApiError as err:
            print(f"Error fetching match info for match ID {match_id}: {err}")

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
        if created:
            print(f"{match} created")
        else:
            print(f"{match} already exists")
        return match, created

    def create_summoner_match(self, info_dict, game_creation):
        icon_id = info_dict["profileIcon"]
        try:
            icon = ProfileIcon.objects.get(profile_id=icon_id)
        except ProfileIcon.DoesNotExist:
            print("Profile icon {icon_id} does not exist")
            icon = None
        summoner_exist = Summoner.objects.filter(puuid=info_dict["puuid"])
        if summoner_exist and summoner_exist[0].last_updated and game_creation < summoner_exist[0].last_updated:
            print(f"Do not need to update {summoner_exist[0]}")
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
        if created:
            print(f"{summoner} created")
        else:
            print(f"{summoner} already exists")
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
                    print(f"Item with ID {item_id} does not exist.")

    def _increment_models(self, participant, match, snowballs):
        patch = match.get_patch()
        year = match.game_start.year
        summoner_champ_stats, createad = SummonerChampionStats.objects.update_or_create(
            summoner=participant.summoner,
            champion=participant.champion,
            year=year
        )
        summoner_champ_stats.update_stats(participant, match)
        print(f"{summoner_champ_stats} created") if createad else print(f"{summoner_champ_stats} already exists")

        account_stats, created = AccountStats.objects.update_or_create(
            summoner=participant.summoner,
            year=year
        )
        print(f"{account_stats} created") if created else print(f"{account_stats} already exists")
        account_stats.update_stats(participant, snowballs)

        champ_stats_patch, created = ChampionStatsPatch.objects.update_or_create(
            champion=participant.champion,
            patch=patch
        )
        champ_stats_patch.update_stats(participant)
        print(f"{champ_stats_patch} created") if created else print(f"{champ_stats_patch} already exists")

    def _create_participants(self, match_info: dict, match: Match):
        participants_puid = match_info["metadata"]["participants"]

        for i in range(len(participants_puid)):
            participant_data = match_info["info"]["participants"][i]
            summoner: Summoner = self.create_summoner_match(participant_data, match.game_start)
            champion: Champion = Champion.objects.get(champion_id__iexact=participant_data["championName"])
            team_id = participant_data["teamId"]
            win = True if participant_data["win"] is True else False
            spell1 = SummonerSpell.objects.get(spell_id=participant_data["summoner1Id"])
            spell2 = SummonerSpell.objects.get(spell_id=participant_data["summoner2Id"])
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
            total_snowballs = 0
            if participant.spell1.spell_id == 32:
                total_snowballs = participant_data["summoner1Casts"]
            elif participant.spell2.spell_id == 32:
                total_snowballs = participant_data["summoner2Casts"]
            snowball_hits = participant_data["challenges"]['snowballsHit']
            snowballs = (snowball_hits, total_snowballs)

            if created:
                print(f"{participant} added to match {match}")
            else:
                print(f"{participant} already exists ERORR!!!!")
            self._add_items(participant, participant_data)

            self._increment_models(participant, match, snowballs)

    def process_matches(self, progress_recorder=None):
        self._matches = self._get_all()
        with transaction.atomic():
            total_matches = len(self._matches)
            self._summoner.being_parsed = True
            self._summoner.total_matches = total_matches
            self._summoner.save()

        for i, match in enumerate(self._matches):
            with transaction.atomic():
                if not Match.objects.filter(match_id=match).exists():
                    match_info = self._get_match_info(match)
                    match_model, created = self._create_match(match, match_info["info"])
                    self._create_participants(match_info, match_model)
                else:
                    print(f"{match} already exists")
                self._processed_matches += 1
                self._summoner.parsed_matches += 1;
                print(f"{self._processed_matches} matches processed")
                if progress_recorder:
                    print(i)
                    print(f"{total_matches} total")
                    progress_recorder.set_progress(
                        self._summoner.parsed_matches,
                        self._summoner.total_matches,
                        description="matches processed")
                    self._summoner.save()

        with transaction.atomic():
            self._summoner.being_parsed = False
            self._summoner.save()

    def last_20(self, progress_recorder=None):
        self._matches = self._get_20()
        total_matches = len(self._matches)

        for i, match in enumerate(self._matches):
            print("here")
            with transaction.atomic():
                if not Match.objects.filter(match_id=match).exists():
                    match_info = self._get_match_info(match)
                    match_model, created = self._create_match(match, match_info["info"], new=True)
                    self._create_participants(match_info, match_model)
                else:
                    print(f"{match} already exists")
                print(f"{i} matches processed")
                if progress_recorder:
                    progress_recorder.set_progress(i,total_matches,description="matches processed")




if __name__ == "__main__":
    summonerBuilder = SummonerManager("americas", "na1")
    summonertest = summonerBuilder.create_summoner("kittykatmarco", 'na1')
    matchBuilder = MatchManager("americas", "na1", summonertest)
    matchBuilder.process_matches()
    # summoners = Summoner.objects.all()
    # for i in range(35):
    #     matchMaker = MatchManager("americas", "na1", summoners[i])
    #     matchMaker.process_matches()
    #     print("hey")
