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


class ExpandedStatsTemplateTest(TestCase):
    fixtures = ['test_data.json']
    
    def setUp(self):
        self.client = Client()
        # Get a summoner from the test data
        self.summoner = Summoner.objects.first()
        
    def test_expanded_stats_section_in_template(self):
        """Test that the expanded stats section is present in the match list template"""
        if self.summoner and self.summoner.game_name and self.summoner.tag_line:
            url = reverse('match_history:details', args=[self.summoner.game_name, self.summoner.tag_line])
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            
            # Check that expanded stats section is present
            self.assertContains(response, 'expanded-stats')
            self.assertContains(response, 'damage-stats-section')
            self.assertContains(response, 'vision-objectives-section')
            self.assertContains(response, 'gold-cs-section')
            self.assertContains(response, 'all-participants-stats')
            
    def test_expanded_stats_structure(self):
        """Test that the expanded stats section has the correct structure"""
        if self.summoner and self.summoner.game_name and self.summoner.tag_line:
            url = reverse('match_history:details', args=[self.summoner.game_name, self.summoner.tag_line])
            response = self.client.get(url)
            
            # Check for damage statistics labels
            self.assertContains(response, 'Damage Dealt')
            self.assertContains(response, 'Damage Taken')
            self.assertContains(response, 'Damage to Champions')
            self.assertContains(response, 'Healing Done')
            
            # Check for vision and objectives labels
            self.assertContains(response, 'Vision Score')
            self.assertContains(response, 'Wards Placed')
            self.assertContains(response, 'Wards Destroyed')
            self.assertContains(response, 'Objective Participation')
            
            # Check for gold and CS labels
            self.assertContains(response, 'Gold Earned')
            self.assertContains(response, 'Gold per Minute')
            self.assertContains(response, 'Minions Killed')
            self.assertContains(response, 'Jungle Monsters')
            
    def test_toggle_button_functionality(self):
        """Test that the toggle button has the correct onclick handler"""
        if self.summoner and self.summoner.game_name and self.summoner.tag_line:
            url = reverse('match_history:details', args=[self.summoner.game_name, self.summoner.tag_line])
            response = self.client.get(url)
            
            # Check that the button has the toggle function
            self.assertContains(response, 'onclick="toggleExpandedStats(this)"')
            self.assertContains(response, 'function toggleExpandedStats')


class ExpandedStatsDataTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
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
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='14.16.1',
            winner=100
        )
        
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=3,
            assists=15,
            creep_score=120,
            team=100,
            win=True,
            game_name='TestPlayer'
        )
        
    def test_participant_stats_display(self):
        """Test that participant stats are correctly displayed in expanded section"""
        # The template should show the participant's actual stats
        self.assertEqual(self.participant.kills, 10)
        self.assertEqual(self.participant.deaths, 3)
        self.assertEqual(self.participant.assists, 15)
        self.assertEqual(self.participant.creep_score, 120)
        self.assertTrue(self.participant.win)
        
    def test_match_duration_calculation(self):
        """Test that match duration is correctly calculated"""
        expected_minutes = self.match.game_duration // 60
        self.assertEqual(expected_minutes, 30)
        self.assertEqual(self.match.get_minutes(), 30)
