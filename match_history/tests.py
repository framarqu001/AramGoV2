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
            game_name='testSummoner'
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        expected_str = 'testSummoner playing Aatrox in match match_001'
        self.assertEqual(str(self.participant), expected_str)

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_summoner(self):
        self.summoner.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_champion(self):
        self.champion.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())


class ExpandedMatchCardTest(TestCase):
    def setUp(self):
        # Set up test data for expanded match card functionality
        self.client = Client()
        
        # Create test summoner
        self.summoner = Summoner.objects.create(
            puuid='test-summoner-id',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=50
        )
        
        # Create test champions
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
        
        # Create test match
        self.match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='13.15.1',
            winner=100
        )
        
        # Create test participants
        self.main_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion1,
            kills=12,
            deaths=3,
            assists=15,
            creep_score=180,
            team=100,
            win=True,
            game_name='TestPlayer'
        )
        
        # Create additional participant for team
        self.other_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,  # Using same summoner for simplicity
            champion=self.champion2,
            kills=8,
            deaths=5,
            assists=12,
            creep_score=150,
            team=200,
            win=False,
            game_name='OtherPlayer'
        )

    def test_match_card_template_contains_expanded_section(self):
        """Test that the match list template contains the expanded participant stats section"""
        from django.template.loader import render_to_string
        
        # Prepare context data similar to what the view provides
        blue_team = [self.main_participant]
        red_team = [self.other_participant]
        main_stats = {
            'kda': '9.00',
            'cs_min': '6.0'
        }
        
        matches = [(self.match, self.main_participant, blue_team, red_team, main_stats)]
        
        # Render the template
        rendered_html = render_to_string('match_history/match_list.html', {'matches': matches})
        
        # Check for expanded section elements
        self.assertIn('participant-stats-expanded', rendered_html)
        self.assertIn('participant-detailed-entry', rendered_html)
        self.assertIn('team-blue-stats', rendered_html)
        self.assertIn('team-red-stats', rendered_html)
        self.assertIn('participant-champion', rendered_html)
        self.assertIn('participant-build', rendered_html)
        self.assertIn('participant-items', rendered_html)
        self.assertIn('participant-stats', rendered_html)

    def test_match_button_has_toggle_attributes(self):
        """Test that the match button has proper attributes for expand/collapse functionality"""
        from django.template.loader import render_to_string
        
        blue_team = [self.main_participant]
        red_team = [self.other_participant]
        main_stats = {'kda': '9.00', 'cs_min': '6.0'}
        matches = [(self.match, self.main_participant, blue_team, red_team, main_stats)]
        
        rendered_html = render_to_string('match_history/match_list.html', {'matches': matches})
        
        # Check for toggle functionality attributes
        self.assertIn('onclick="toggleMatchDetails(this)"', rendered_html)
        self.assertIn('aria-expanded="false"', rendered_html)
        self.assertIn('aria-label="Toggle match details"', rendered_html)

    def test_participant_stats_display_correctly(self):
        """Test that participant statistics are displayed correctly in the expanded section"""
        from django.template.loader import render_to_string
        
        blue_team = [self.main_participant]
        red_team = [self.other_participant]
        main_stats = {'kda': '9.00', 'cs_min': '6.0'}
        matches = [(self.match, self.main_participant, blue_team, red_team, main_stats)]
        
        rendered_html = render_to_string('match_history/match_list.html', {'matches': matches})
        
        # Check for participant stats
        self.assertIn('12/3/15', rendered_html)  # Main participant KDA
        self.assertIn('8/5/12', rendered_html)   # Other participant KDA
        self.assertIn('180 CS', rendered_html)   # Main participant CS
        self.assertIn('150 CS', rendered_html)   # Other participant CS

    def test_team_labels_show_correct_win_status(self):
        """Test that team labels correctly show victory/defeat status"""
        from django.template.loader import render_to_string
        
        blue_team = [self.main_participant]
        red_team = [self.other_participant]
        main_stats = {'kda': '9.00', 'cs_min': '6.0'}
        matches = [(self.match, self.main_participant, blue_team, red_team, main_stats)]
        
        rendered_html = render_to_string('match_history/match_list.html', {'matches': matches})
        
        # Check for team victory/defeat labels
        self.assertIn('Blue Team (Victory)', rendered_html)
        self.assertIn('Red Team (Defeat)', rendered_html)

    def test_main_participant_highlighted(self):
        """Test that the main participant is properly highlighted in the expanded view"""
        from django.template.loader import render_to_string
        
        blue_team = [self.main_participant]
        red_team = [self.other_participant]
        main_stats = {'kda': '9.00', 'cs_min': '6.0'}
        matches = [(self.match, self.main_participant, blue_team, red_team, main_stats)]
        
        rendered_html = render_to_string('match_history/match_list.html', {'matches': matches})
        
        # Check for main participant highlighting
        self.assertIn('main-participant', rendered_html)
        self.assertIn('highlight', rendered_html)


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
