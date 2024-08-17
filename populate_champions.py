import os

import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "AramGoV2.settings")
django.setup()

from match_history.models import Champion, Item, ProfileIcon

RIOT_API_KEY = "RGAPI-694e1a5c-5426-4aa6-8f9a-8e9e3502fb47"


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


def populate_items(item_data: dict):
    print("Populating items")
    for id, info in item_data.items():
        item_id = id
        name = info["name"]
        image = info["image"]["full"]
        _, created = Item.objects.update_or_create(
            item_id=id,
            defaults={
                "item_id": item_id,
                "name": name,
                "image_path": image
            }
        )
        if created:
            print(f"Added {name} to the database.")
        else:
            print(f"Updated {name} in the database.")


def populate_profileicon(profileicon_data: dict):
    print("Populating profileicon")
    for id, info in profileicon_data.items():
        profile_id = id
        image = info["image"]["full"]
        _, created = ProfileIcon.objects.update_or_create(
            profile_id=profile_id,
            defaults={
                "image_path": image
            }
        )
        if created:
            print(f"Added {id} to the database.")
        else:
            print(f"Updated {id} in the database.")


def get_patch():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(url)
    response = response.json()
    return response[0]


def data(url):
    response = requests.get(url)
    response = response.json()
    return response["data"]


if __name__ == "__main__":
    patch = get_patch()
    item_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    profile_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/profileicon.json"
    champion_data = data(champion_url)
    item_data = data(item_url)
    profile_data = data(profile_url)

    populate_champions(champion_data)
    populate_items(item_data)
    populate_profileicon(profile_data)
