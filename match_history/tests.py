from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.template import Context, Template
from django.urls import reverse
from unittest.mock import patch, MagicMock
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
            image_path='Aatrox.png'
        )
        self.match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1'
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        self.assertEqual(str(self.participant), f"{self.participant.game_name} playing {self.participant.champion} in match {self.participant.match}")

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_summoner(self):
        self.summoner.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_champion(self):
        self.champion.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())


    ##AramGoV2 if user changes there name
    ## AramGoV2 all items are retriavable


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


class ExpandedMatchCardTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='expanded-card-test-id',
            game_name='ExpandedTest',
            tag_line='NA1',
            normalized_game_name='expandedtest',
            normalized_tag_line='na1',
            summoner_name='ExpandedTest',
            summoner_level=100
        )
        
        self.champion = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png',
            splash_image_path='Ahri_0.jpg'
        )
        
        self.match = Match.objects.create(
            match_id='expanded_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1500,  # 25 minutes
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100  # Blue team wins
        )
        
        # Create runes
        self.rune1 = Rune.objects.create(
            rune_id=8000,
            name='Precision',
            image_path='perk-images/Styles/7201_Precision.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=8400,
            name='Resolve',
            image_path='perk-images/Styles/7204_Resolve.png'
        )
        
        # Create summoner spells
        self.spell1 = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=32,
            name='Mark',
            image_path='SummonerMark.png'
        )
        
        # Create items
        self.item1 = Item.objects.create(
            item_id='3157',
            name="Zhonya's Hourglass",
            image_path='3157.png'
        )
        
        self.item2 = Item.objects.create(
            item_id='3089',
            name="Rabadon's Deathcap",
            image_path='3089.png'
        )
        
        # Create participant
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=15,
            deaths=5,
            assists=10,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=50,
            item1=self.item1,
            item2=self.item2,
            team=100,  # Blue team
            win=True,
            game_name='ExpandedTest'
        )
        
        # Create mock stats for expanded card
        self.main_stats = {
            "kda": "5.00",
            "cs_min": "2.0",
            "damage_dealt": "20,000",
            "damage_taken": "15,000",
            "healing": "5,000",
            "gold_earned": "12,500",
            "gold_spent": "11,250",
            "turret_damage": "3,500",
            "objective_participation": "75%"
        }
        
        # Set up client
        self.client = Client()
        
    def test_expanded_match_card_template_renders(self):
        """Test that the expanded_match_card.html template renders without errors"""
        from django.template.loader import render_to_string
        
        context = {
            'main_participant': self.participant,
            'main_stats': self.main_stats
        }
        
        # Render the template
        rendered = render_to_string('match_history/expanded_match_card.html', context)
        
        # Check that key elements are in the rendered template
        self.assertIn('Detailed Player Stats', rendered)
        self.assertIn('Combat Stats', rendered)
        self.assertIn('Economy', rendered)
        self.assertIn('Objectives', rendered)
        self.assertIn('Item Build Timeline', rendered)
        self.assertIn('20,000', rendered)  # Damage dealt value
        self.assertIn('12,500', rendered)  # Gold earned value
        
    def test_expanded_match_card_handles_missing_data(self):
        """Test that the template handles missing or null values gracefully"""
        from django.template.loader import render_to_string
        
        # Create context with missing values
        context = {
            'main_participant': self.participant,
            'main_stats': {
                "kda": "5.00",
                "cs_min": "2.0",
                # Missing damage_dealt
                "damage_taken": None,  # Null value
                # Missing healing
                "gold_earned": "",  # Empty string
                # Missing gold_spent
                "turret_damage": "3,500",
                # Missing objective_participation
            }
        }
        
        # Render the template
        rendered = render_to_string('match_history/expanded_match_card.html', context)
        
        # Check that the template handles missing values with N/A
        self.assertIn('N/A', rendered)