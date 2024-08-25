import os

import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "test.settings")
django.setup()

from match_history.models import Champion, Item, ProfileIcon, SummonerSpell, Rune

RIOT_API_KEY = "RGAPI-d5b99d98-824c-4459-83c1-6f68edfff7e7"


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

def populate_spells(spell_data: dict):
    print("Populating spells")
    for info in spell_data.values():
        spell_id = int(info["key"])
        name = info["name"]
        image = info["image"]["full"]
        spell, created = SummonerSpell.objects.get_or_create(
            spell_id=spell_id,
            defaults={
                "name": name,
                "image_path": image
            }
        )
        if created:
            print(f"Added {name} to the database.")
        else:
            print(f"Updated {name} in the database.")

def populate_runes(runes_data: dict):
    print("populating runes")
    for category in runes_data:
        category_id = category["id"]
        category_name = category["name"]
        category_image = category["icon"]
        rune, created = Rune.objects.get_or_create(
            rune_id = category_id,
            defaults={
                "name": category_name,
                "image_path": category_image
            }
        )
        if created:
            print(f"Added {category_name} to the database.")
        else:
            print(f"Updated {category_name} in the database.")

        print(f"Rune Category: {category['name']}")
        for slot in category['slots']:
            for rune in slot['runes']:
                rune_id = rune['id']
                name = rune["name"]
                image_path = rune["icon"]
                rune, created = Rune.objects.get_or_create(
                    rune_id = rune_id,
                    defaults={
                        "name": name,
                        "image_path": image_path
                    }
                )
                if created:
                    print(f"Added {name} to the database.")
                else:
                    print(f"Updated {name} in the database.")

    

def get_patch():
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(url)
    response = response.json()
    return response[0]


def data(url):
    response = requests.get(url)
    response = response.json()
    return response["data"]

def rune_data(url):
    response = requests.get(url)
    response = response.json()
    return response


if __name__ == "__main__":
    patch = get_patch()
    item_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"
    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    profile_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/profileicon.json"
    spells_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/summoner.json"
    runes_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/runesReforged.json"
    champion_data = data(champion_url)
    item_data = data(item_url)
    profile_data = data(profile_url)
    spell_data = data(spells_url)
    runes_data = rune_data(runes_url)

    populate_champions(champion_data)
    populate_items(item_data)
    populate_profileicon(profile_data)
    populate_spells(spell_data)
    populate_runes(runes_data);
