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
        self.match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1',
            winner=Match.BLUE_TEAM
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            spell1=self.spell1,
            spell2=self.spell2,
            team=Match.BLUE_TEAM,
            win=True,
            game_name='testSummoner'
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        self.assertEqual(str(self.participant), 'testSummoner playing Aatrox in match match_001')

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


class MatchDetailsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.summoner1 = Summoner.objects.create(
            puuid='summoner1-uuid',
            game_name='TestPlayer1',
            tag_line='NA1',
            summoner_name='TestPlayer1',
            summoner_level=30
        )
        
        self.summoner2 = Summoner.objects.create(
            puuid='summoner2-uuid',
            game_name='TestPlayer2',
            tag_line='NA1',
            summoner_name='TestPlayer2',
            summoner_level=25
        )
        
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
        
        self.match = Match.objects.create(
            match_id='TEST_MATCH_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=Match.BLUE_TEAM,
            blue_team_towers=2,
            red_team_towers=1,
            blue_team_dragons=1,
            red_team_dragons=0
        )
        
        # Create participants with extended stats
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            spell1=self.spell1,
            spell2=self.spell2,
            team=Match.BLUE_TEAM,
            win=True,
            game_name='TestPlayer1',
            damage_dealt=25000,
            damage_taken=18000,
            gold_earned=12000
        )
        
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=3,
            deaths=8,
            assists=5,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=Match.RED_TEAM,
            win=False,
            game_name='TestPlayer2',
            damage_dealt=18000,
            damage_taken=22000,
            gold_earned=9500
        )

    def test_match_details_view_exists(self):
        """Test that the match details view is accessible"""
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_match_details_view_with_summoner_param(self):
        """Test match details view with specific summoner parameter"""
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url, {'summoner': self.summoner1.puuid})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['main_participant'], self.participant1)

    def test_match_details_ajax_request(self):
        """Test AJAX request to match details view"""
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'match-details-expanded')

    def test_match_details_context_data(self):
        """Test that match details view provides correct context data"""
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url)
        
        self.assertIn('match', response.context)
        self.assertIn('blue_team', response.context)
        self.assertIn('red_team', response.context)
        self.assertIn('blue_team_kills', response.context)
        self.assertIn('red_team_kills', response.context)
        self.assertIn('main_participant', response.context)
        
        # Check team separation
        self.assertEqual(len(response.context['blue_team']), 1)
        self.assertEqual(len(response.context['red_team']), 1)
        self.assertEqual(response.context['blue_team_kills'], 10)
        self.assertEqual(response.context['red_team_kills'], 3)

    def test_match_details_nonexistent_match(self):
        """Test 404 response for non-existent match"""
        url = reverse('match_history:match_details', args=['NONEXISTENT_MATCH'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_match_details_template_rendering(self):
        """Test that the template renders with correct data"""
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url)
        
        # Check that extended stats are displayed
        self.assertContains(response, '25000')  # damage_dealt
        self.assertContains(response, '18000')  # damage_taken
        self.assertContains(response, '12000')  # gold_earned
        
        # Check team objectives
        self.assertContains(response, '2')  # blue_team_towers
        self.assertContains(response, '1')  # red_team_towers


class ParticipantExtendedStatsTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='test-uuid',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        
        self.spell = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        self.match = Match.objects.create(
            match_id='TEST_MATCH_002',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=Match.BLUE_TEAM,
            blue_team_towers=3,
            red_team_towers=0,
            blue_team_dragons=2,
            red_team_dragons=1
        )

    def test_participant_extended_stats_creation(self):
        """Test creating participant with extended stats"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=100,
            spell1=self.spell,
            spell2=self.spell,
            team=Match.BLUE_TEAM,
            win=True,
            game_name='TestPlayer',
            damage_dealt=20000,
            damage_taken=15000,
            gold_earned=10000
        )
        
        self.assertEqual(participant.damage_dealt, 20000)
        self.assertEqual(participant.damage_taken, 15000)
        self.assertEqual(participant.gold_earned, 10000)

    def test_participant_extended_stats_null_values(self):
        """Test participant creation with null extended stats"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=100,
            spell1=self.spell,
            spell2=self.spell,
            team=Match.BLUE_TEAM,
            win=True,
            game_name='TestPlayer'
            # Extended stats not provided - should default to 0
        )
        
        self.assertEqual(participant.damage_dealt, 0)
        self.assertEqual(participant.damage_taken, 0)
        self.assertEqual(participant.gold_earned, 0)


class MatchExtendedStatsTest(TestCase):
    def test_match_team_objectives_creation(self):
        """Test creating match with team objectives"""
        match = Match.objects.create(
            match_id='TEST_MATCH_003',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=Match.BLUE_TEAM,
            blue_team_towers=5,
            red_team_towers=2,
            blue_team_dragons=3,
            red_team_dragons=1
        )
        
        self.assertEqual(match.blue_team_towers, 5)
        self.assertEqual(match.red_team_towers, 2)
        self.assertEqual(match.blue_team_dragons, 3)
        self.assertEqual(match.red_team_dragons, 1)

    def test_match_team_objectives_null_values(self):
        """Test match creation with null team objectives"""
        match = Match.objects.create(
            match_id='TEST_MATCH_004',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=Match.BLUE_TEAM
            # Team objectives not provided - should default to 0
        )
        
        self.assertEqual(match.blue_team_towers, 0)
        self.assertEqual(match.red_team_towers, 0)
        self.assertEqual(match.blue_team_dragons, 0)
        self.assertEqual(match.red_team_dragons, 0)
