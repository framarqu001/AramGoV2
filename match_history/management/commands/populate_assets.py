
import requests
from django.core.cache import cache
from django.core.management.base import BaseCommand
from match_history.models import Champion, Item, ProfileIcon, SummonerSpell, Rune

patch = cache.get("PATCH")


class Command(BaseCommand):
    help = 'Populates the database with data from Riot API'

    def handle(self, *args, **options):
        patch = cache.get("PATCH")
        self.stdout.write("Starting data population...")
        self.populate(patch)

    def data(self, url):
        response = requests.get(url)
        response = response.json()
        return response["data"]

    def rune_data(self, url):
        response = requests.get(url)
        response = response.json()
        return response

    def populate(self, patch):
        item_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"
        champion_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
        profile_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/profileicon.json"
        spells_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/summoner.json"
        runes_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/runesReforged.json"

        champion_data = self.data(champion_url)
        item_data = self.data(item_url)
        profile_data = self.data(profile_url)
        spell_data = self.data(spells_url)
        runes_data = self.rune_data(runes_url)

        self.populate_champions(champion_data)
        self.populate_items(item_data)
        self.populate_profileicon(profile_data)
        self.populate_spells(spell_data)
        self.populate_runes(runes_data)

    def populate_champions(self, champion_data: dict):
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
                    "image_path": champion_square_image,
                    "splash_image_path": f"{champion_id}_0.jpg",
                }
            )
            if created:
                print(f"Added {champion_name} to the database.")
            else:
                print(f"Updated {champion_name} in the database.")

    def populate_items(self, item_data: dict):
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

    def populate_profileicon(self, profileicon_data: dict):
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

    def populate_spells(self, spell_data: dict):
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

    def populate_runes(self, runes_data: dict):
        print("populating runes")
        for category in runes_data:
            category_id = category["id"]
            category_name = category["name"]
            category_image = category["icon"]
            rune, created = Rune.objects.get_or_create(
                rune_id=category_id,
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
                        rune_id=rune_id,
                        defaults={
                            "name": name,
                            "image_path": image_path
                        }
                    )
                    if created:
                        print(f"Added {name} to the database.")
                    else:
                        print(f"Updated {name} in the database.")
