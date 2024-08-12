import os

import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()

from match_history.models import Champion

RIOT_API_KEY = "RGAPI-54e80c8c-87b4-4e6e-a32a-749aa093116c"


def get_patch():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(url)
    response = response.json()
    return response[0]


def get_champion_data(patch):
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    response = requests.get(url)
    response = response.json()
    return response["data"]


def populate_champions(champion_data: dict):
    print("Populating champions")
    for info in champion_data.values():
        champion_id = info["id"]
        champion_name = info["name"]
        champion_title = info["title"]
        champion_square_image = info["image"]["full"]
        _, created = Champion.objects.update_or_create(
            champion_id=champion_id,
            defaults={
                "name": champion_name,
                "title": champion_title,
                "image_path": champion_square_image
            }
        )
        if created:
            print(f"Added {champion_name} to the database.")
        else:
            print(f"Updated {champion_name} in the database.")


if __name__ == "__main__":
    patch = get_patch()
    champion_data = get_champion_data(patch)
    populate_champions(champion_data)
