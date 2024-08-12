import os

import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()

from match_history.models import *

RIOT_API_KEY = "RGAPI-54e80c8c-87b4-4e6e-a32a-749aa093116c"
routing = "americas"
BASE_URL = f"https://{routing}.api.riotgames.com/"


def get_matches(url):
    pass


def get_puid(summoner_name, tag):
    url = f"{BASE_URL}riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    response = response.json();
    return response["puuid"]


def get_account_info(puid):
    url = f"{BASE_URL}lol/summoner/v4/summoners/by-puuid/{puid}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    response = response.json();
    return response


def create_summoner(summoner_name, tag):
    puid = get_puid(summoner_name, tag)
    account_info = get_account_info(puid)
    level = account_info["summonerLevel"]
    icon_id = account_info["profileIconId"]
    icon = ProfileIcon.objects.get(id=icon_id)
    _, created = Summoner.objects.create(
        puid=puid,
        game_name=summoner_name,
        tagline=tag,
        summonerLevel=level,
        profile_icon=icon
    )


if __name__ == "__main__":
    create_summoner("highkeysavage", "NA1")
