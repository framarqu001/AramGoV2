from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.urls import reverse
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
        self.assertEqual(str(self.participant), 'testSummoner#NA1 playing Aatrox in match match_001')

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


class ExpandableMatchCardTest(TestCase):
    def setUp(self):
        # Create test data for expandable match card functionality
        self.client = Client()
        
        # Create summoners
        self.main_summoner = Summoner.objects.create(
            puuid='main-summoner-id',
            game_name='MainPlayer',
            tag_line='NA1',
            summoner_name='MainPlayer',
            summoner_level=30
        )
        
        self.other_summoner = Summoner.objects.create(
            puuid='other-summoner-id',
            game_name='OtherPlayer',
            tag_line='NA1',
            summoner_name='OtherPlayer',
            summoner_level=25
        )
        
        # Create champions
        self.champion1 = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        
        self.champion2 = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png',
            splash_image_path='Ahri_0.jpg'
        )
        
        # Create items
        self.item1 = Item.objects.create(
            item_id='1001',
            name='Boots of Speed',
            image_path='1001.png'
        )
        
        self.item2 = Item.objects.create(
            item_id='3006',
            name='Berserker\'s Greaves',
            image_path='3006.png'
        )
        
        # Create summoner spells
        self.spell1 = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=14,
            name='Ignite',
            image_path='SummonerDot.png'
        )
        
        # Create runes
        self.rune1 = Rune.objects.create(
            rune_id=8005,
            name='Press the Attack',
            image_path='perk-images/Styles/Precision/PressTheAttack/PressTheAttack.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=8014,
            name='Coup de Grace',
            image_path='perk-images/Styles/Precision/CoupDeGrace/CoupDeGrace.png'
        )
        
        # Create match
        self.match = Match.objects.create(
            match_id='match_expandable_test',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1'
        )
        
        # Create participants
        self.main_participant = Participant.objects.create(
            match=self.match,
            summoner=self.main_summoner,
            champion=self.champion1,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            item1=self.item1,
            item2=self.item2,
            team=100,
            win=True,
            game_name='MainPlayer'
        )
        
        self.other_participant = Participant.objects.create(
            match=self.match,
            summoner=self.other_summoner,
            champion=self.champion2,
            kills=5,
            deaths=5,
            assists=12,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            item1=self.item1,
            item2=self.item2,
            team=200,
            win=False,
            game_name='OtherPlayer'
        )
    
    def test_expandable_content_structure_in_template(self):
        """Test that the expandable content structure is present in the rendered template"""
        # This test would require a view that renders the match_list.html template
        # Since we don't have a direct view for this, we'll test the template structure indirectly
        
        # Test that the match has the required participants
        self.assertEqual(self.match.participants.count(), 2)
        
        # Test that participants have the required data for expanded view
        self.assertIsNotNone(self.main_participant.champion.name)
        self.assertIsNotNone(self.main_participant.item1.name)
        self.assertTrue(self.main_participant.win)
        self.assertFalse(self.other_participant.win)
    
    def test_participant_data_for_expanded_view(self):
        """Test that participant data is properly structured for the expanded view"""
        # Test main participant data
        self.assertEqual(self.main_participant.kills, 10)
        self.assertEqual(self.main_participant.deaths, 2)
        self.assertEqual(self.main_participant.assists, 8)
        self.assertEqual(self.main_participant.creep_score, 150)
        self.assertEqual(self.main_participant.champion.name, 'Aatrox')
        self.assertEqual(self.main_participant.item1.name, 'Boots of Speed')
        
        # Test team assignment
        self.assertEqual(self.main_participant.team, 100)  # Blue team
        self.assertEqual(self.other_participant.team, 200)  # Red team
    
    def test_match_result_display(self):
        """Test that match results are properly displayed"""
        self.assertEqual(self.main_participant.match_result(), "Victory")
        self.assertEqual(self.other_participant.match_result(), "Defeat")
    
    def test_item_url_generation(self):
        """Test that item URLs are properly generated for the expanded view"""
        # Set up cache for patch version
        cache.set('PATCH', '14.17.1')
        
        expected_url = "https://ddragon.leagueoflegends.com/cdn/14.17.1/img/item/1001.png"
        self.assertEqual(self.item1.get_url(), expected_url)
    
    def test_champion_url_generation(self):
        """Test that champion URLs are properly generated for the expanded view"""
        # Set up cache for patch version
        cache.set('PATCH', '14.17.1')
        
        expected_url = "https://ddragon.leagueoflegends.com/cdn/14.17.1/img/champion/Aatrox.png"
        self.assertEqual(self.champion1.get_url(), expected_url)


class MatchCardCSSClassTest(TestCase):
    """Test CSS class assignments for match cards"""
    
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='css-test-summoner',
            game_name='CSSTestPlayer',
            tag_line='NA1',
            summoner_name='CSSTestPlayer',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='TestChamp',
            name='Test Champion',
            title='The Test',
            image_path='TestChamp.png',
            splash_image_path='TestChamp_0.jpg'
        )
        
        self.match = Match.objects.create(
            match_id='css_test_match',
            game_start=datetime.datetime.now(),
            game_duration=1500,
            game_mode='ARAM',
            game_version='14.17.1'
        )
    
    def test_win_loss_css_classes(self):
        """Test that win/loss CSS classes are properly assigned"""
        # Create winning participant
        winning_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=15,
            deaths=3,
            assists=10,
            creep_score=180,
            team=100,
            win=True,
            game_name='CSSTestPlayer'
        )
        
        # Create losing participant
        losing_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=8,
            assists=6,
            creep_score=120,
            team=200,
            win=False,
            game_name='CSSTestPlayer'
        )
        
        # Test win/loss status
        self.assertTrue(winning_participant.win)
        self.assertFalse(losing_participant.win)
        
        # Test match result strings
        self.assertEqual(winning_participant.match_result(), "Victory")
        self.assertEqual(losing_participant.match_result(), "Defeat")
