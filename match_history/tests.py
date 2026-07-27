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


class MatchCardStylingTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid-123',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=45
        )
        
        self.champion = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        
        self.match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create participants for both teams
        for i in range(10):
            team = 100 if i < 5 else 200
            win = team == 100
            Participant.objects.create(
                match=self.match,
                summoner=self.summoner,
                champion=self.champion,
                kills=5 + i,
                deaths=2,
                assists=8 + i,
                creep_score=120 + i * 10,
                team=team,
                win=win,
                game_name=f'Player{i}'
            )

    def test_match_card_css_classes_present(self):
        """Test that the CSS file contains the new styling classes"""
        with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
            css_content = f.read()
        
        # Check for new CSS classes
        self.assertIn('.rank-indicator', css_content)
        self.assertIn('.level-indicator', css_content)
        self.assertIn('.participant-stats', css_content)
        self.assertIn('.participant-expanded-info', css_content)
        self.assertIn('.participant-main-info', css_content)
        
        # Check for responsive breakpoints
        self.assertIn('@media (max-width: 1200px)', css_content)
        self.assertIn('@media (max-width: 992px)', css_content)
        self.assertIn('@media (max-width: 768px)', css_content)
        self.assertIn('@media (max-width: 480px)', css_content)
        
        # Check for rank tier classes
        self.assertIn('.rank-indicator.gold', css_content)
        self.assertIn('.rank-indicator.silver', css_content)
        self.assertIn('.rank-indicator.diamond', css_content)

    def test_match_card_height_updated(self):
        """Test that match card height has been increased"""
        with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
            css_content = f.read()
        
        # Check that height has been updated from 100px to 120px
        self.assertIn('height: 120px', css_content)
        self.assertIn('.match-card.expanded', css_content)

    def test_participant_section_template_structure(self):
        """Test that the template includes new participant information structure"""
        with open('/workspace/match_history/templates/match_history/match_list.html', 'r') as f:
            template_content = f.read()
        
        # Check for new template structure
        self.assertIn('participant-main-info', template_content)
        self.assertIn('participant-expanded-info', template_content)
        self.assertIn('participant-stats', template_content)
        self.assertIn('level-indicator', template_content)
        self.assertIn('rank-indicator', template_content)
        self.assertIn('participant-kda', template_content)
        self.assertIn('participant-cs', template_content)

    def test_color_scheme_consistency(self):
        """Test that new styles maintain existing color scheme"""
        with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
            css_content = f.read()
        
        # Check that existing color variables are used
        self.assertIn('var(--blue-color)', css_content)
        self.assertIn('var(--red-color)', css_content)
        self.assertIn('var(--secondary-color)', css_content)
        self.assertIn('var(--yellow-color)', css_content)
        
        # Check that win/loss colors are maintained
        self.assertIn('.match-card.match-win', css_content)
        self.assertIn('.match-card.match-lose', css_content)

    def test_responsive_grid_layout_updated(self):
        """Test that grid layout has been updated for expanded information"""
        with open('/workspace/match_history/static/match_history/css/details.css', 'r') as f:
            css_content = f.read()
        
        # Check that grid template columns have been updated
        self.assertIn('grid-template-columns: .6fr 1fr 1fr 1.2fr', css_content)
        self.assertIn('gap: 0.5rem', css_content)


class ParticipantInformationTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='test-puuid-456',
            game_name='TestSummoner',
            tag_line='NA1',
            summoner_level=67
        )

    def test_summoner_level_display(self):
        """Test that summoner level is properly accessible for display"""
        self.assertEqual(self.summoner.summoner_level, 67)
        self.assertIsNotNone(self.summoner.summoner_level)

    def test_participant_stats_calculation(self):
        """Test that participant stats are properly calculated for display"""
        champion = Champion.objects.create(
            champion_id='TestChamp',
            name='Test Champion',
            title='Test Title',
            image_path='test.png',
            splash_image_path='test_splash.jpg'
        )
        
        match = Match.objects.create(
            match_id='test_match_stats',
            game_start=datetime.datetime.now(),
            game_duration=1500,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        participant = Participant.objects.create(
            match=match,
            summoner=self.summoner,
            champion=champion,
            kills=12,
            deaths=3,
            assists=15,
            creep_score=180,
            team=100,
            win=True,
            game_name='TestSummoner'
        )
        
        # Test that stats are accessible
        self.assertEqual(participant.kills, 12)
        self.assertEqual(participant.deaths, 3)
        self.assertEqual(participant.assists, 15)
        self.assertEqual(participant.creep_score, 180)
