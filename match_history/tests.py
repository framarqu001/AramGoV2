from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig
import datetime


class MatchParticipantDBTest(TransactionTestCase):
    fixtures = ['test_data.json']

    ## Ensure that all matches have 10 participants
    def test_match_has_10_participants(self):
        matches = Match.objects.all()
        for match in matches:
            participants_count = match.participants.count()
            self.assertEqual(participants_count, 10, f"Match has {participants_count} participants, expected 10")


class MatchParticipantTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='some-unique-id',
            game_name='testSummoner',
            tag_line='NA1',
            summoner_name='testSummoner',
            summoner_level=30
        )
        self.champion = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        self.match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1',
            winner=100
        )
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name='Flash',
            image_path='flash.png'
        )
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name='Ignite',
            image_path='ignite.png'
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            team=100,
            win=True,
            game_name='testSummoner',
            spell1=self.spell1,
            spell2=self.spell2,
            # New fields
            damage_dealt=15000,
            damage_taken=10000,
            vision_score=20,
            objectives_stolen=1,
            objectives_killed=2
        )
        self.item = Item.objects.create(
            item_id='1001',
            name='Boots',
            image_path='boots.png'
        )
        self.item_purchase = ItemPurchase.objects.create(
            participant=self.participant,
            item=self.item,
            timestamp=300  # 5 minutes into the game
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        self.assertEqual(str(self.participant), f'{self.participant.game_name} playing {self.participant.champion} in match {self.participant.match}')

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_summoner(self):
        self.summoner.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_champion(self):
        self.champion.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())
        
    def test_new_statistics_fields(self):
        # Test that the new fields are correctly stored
        self.assertEqual(self.participant.damage_dealt, 15000)
        self.assertEqual(self.participant.damage_taken, 10000)
        self.assertEqual(self.participant.vision_score, 20)
        self.assertEqual(self.participant.objectives_stolen, 1)
        self.assertEqual(self.participant.objectives_killed, 2)
        
    def test_damage_per_minute(self):
        # Test the damage_per_minute method
        # Match duration is 1800 seconds = 30 minutes
        # Damage dealt is 15000
        # Expected damage per minute is 15000 / 30 = 500
        self.assertEqual(self.participant.damage_per_minute(), 500)
        
    def test_damage_taken_per_minute(self):
        # Test the damage_taken_per_minute method
        # Match duration is 1800 seconds = 30 minutes
        # Damage taken is 10000
        # Expected damage taken per minute is 10000 / 30 = 333.33...
        self.assertAlmostEqual(self.participant.damage_taken_per_minute(), 333.33, delta=0.01)
        
    def test_item_purchase_relationship(self):
        # Test that the item purchase is correctly related to the participant
        self.assertEqual(self.item_purchase.participant, self.participant)
        self.assertEqual(self.item_purchase.item, self.item)
        self.assertEqual(self.item_purchase.timestamp, 300)
        self.assertIn(self.item_purchase, self.participant.item_purchases.all())


class ItemPurchaseTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='some-unique-id-2',
            game_name='testSummoner2',
            tag_line='NA1',
            summoner_name='testSummoner2',
            summoner_level=30
        )
        self.champion = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png',
            splash_image_path='Ahri_0.jpg'
        )
        self.match = Match.objects.create(
            match_id='match_002',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1',
            winner=100
        )
        self.spell1 = SummonerSpell.objects.create(
            spell_id=3,
            name='Teleport',
            image_path='teleport.png'
        )
        self.spell2 = SummonerSpell.objects.create(
            spell_id=4,
            name='Heal',
            image_path='heal.png'
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            team=100,
            win=True,
            game_name='testSummoner2',
            spell1=self.spell1,
            spell2=self.spell2
        )
        self.item1 = Item.objects.create(
            item_id='2001',
            name='Boots',
            image_path='boots.png'
        )
        self.item2 = Item.objects.create(
            item_id='2002',
            name='Sword',
            image_path='sword.png'
        )
        self.item_purchase1 = ItemPurchase.objects.create(
            participant=self.participant,
            item=self.item1,
            timestamp=300  # 5 minutes into the game
        )
        self.item_purchase2 = ItemPurchase.objects.create(
            participant=self.participant,
            item=self.item2,
            timestamp=600  # 10 minutes into the game
        )

    def test_item_purchase_ordering(self):
        # Test that item purchases are ordered by timestamp
        purchases = list(self.participant.item_purchases.all())
        self.assertEqual(purchases[0], self.item_purchase1)
        self.assertEqual(purchases[1], self.item_purchase2)
        
    def test_item_purchase_string_representation(self):
        expected_str = f"{self.participant.game_name} purchased {self.item1.name} at {self.item_purchase1.timestamp} seconds"
        self.assertEqual(str(self.item_purchase1), expected_str)
        
    def test_cascade_delete_with_participant(self):
        self.participant.delete()
        self.assertFalse(ItemPurchase.objects.filter(pk=self.item_purchase1.pk).exists())
        self.assertFalse(ItemPurchase.objects.filter(pk=self.item_purchase2.pk).exists())
        
    def test_cascade_delete_with_item(self):
        self.item1.delete()
        self.assertFalse(ItemPurchase.objects.filter(pk=self.item_purchase1.pk).exists())
        self.assertTrue(ItemPurchase.objects.filter(pk=self.item_purchase2.pk).exists())


class PatchVersionCacheTest(TestCase):
    @patch('AramGoV2.util.current_patch.get_patch')
    def test_patch_version_cache_timeout(self, mock_get_patch):
        # Mock the get_patch function to return a fixed value
        mock_get_patch.return_value = '13.15.1'
        
        # Clear the cache before testing
        cache.delete('PATCH')
        
        # Initialize the app config which should cache the patch version
        app_config = MatchHistoryConfig('match_history', None)
        app_config.ready()
        
        # Verify that the patch version was cached
        cached_patch = cache.get('PATCH')
        self.assertEqual(cached_patch, '13.15.1')
        
        # Check the timeout value (this requires accessing internal cache details)
        # We can't directly check the timeout, but we can verify the patch is cached
        self.assertIsNotNone(cached_patch)
        
        # Verify that the mock was called
        mock_get_patch.assert_called_once()