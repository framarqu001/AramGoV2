from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from django.urls import reverse
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


class ChampionStatsPatchTest(TestCase):
    def setUp(self):
        # Create test data
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
        
        self.patch = '14.17'
        
        # Create matches for the patch
        self.match1 = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version=f'{self.patch}.1',
            winner=100
        )
        self.match2 = Match.objects.create(
            match_id='match_002',
            game_start=datetime.datetime.now(),
            game_duration=1500,
            game_mode='ARAM',
            game_version=f'{self.patch}.2',
            winner=200
        )
        
        # Create champion stats for the patch
        self.stats1 = ChampionStatsPatch.objects.create(
            champion=self.champion1,
            patch=self.patch,
            total_played=100,
            total_wins=60,
            total_losses=40
        )
        self.stats2 = ChampionStatsPatch.objects.create(
            champion=self.champion2,
            patch=self.patch,
            total_played=80,
            total_wins=30,
            total_losses=50
        )
        
        # Clear cache
        cache.clear()
    
    def test_win_rate_calculation(self):
        """Test that win_rate method correctly calculates the win rate."""
        self.assertEqual(self.stats1.win_rate(), 60.0)
        self.assertEqual(self.stats2.win_rate(), 37.5)
        
        # Test edge case with no games played
        empty_stats = ChampionStatsPatch.objects.create(
            champion=self.champion1,
            patch='14.18',
            total_played=0,
            total_wins=0,
            total_losses=0
        )
        self.assertEqual(empty_stats.win_rate(), 0)
    
    @patch('match_history.models.cache.get')
    @patch('match_history.models.cache.set')
    @patch('match_history.models.Match.objects.filter')
    def test_pick_rate_calculation(self, mock_filter, mock_cache_set, mock_cache_get):
        """Test that pick_rate method correctly calculates the pick rate."""
        # Mock cache miss
        mock_cache_get.return_value = None
        
        # Mock match count
        mock_filter_instance = MagicMock()
        mock_filter_instance.count.return_value = 200
        mock_filter.return_value = mock_filter_instance
        
        # Calculate pick rate
        pick_rate1 = self.stats1.pick_rate()
        
        # Verify calculations
        self.assertEqual(pick_rate1, 50.0)  # 100/200 * 100
        
        # Verify cache was set
        mock_cache_set.assert_called_once_with(
            f"total_matches_{self.patch}", 200, timeout=3600
        )
        
        # Test with cached value
        mock_cache_get.return_value = 200
        pick_rate2 = self.stats2.pick_rate()
        self.assertEqual(pick_rate2, 40.0)  # 80/200 * 100
    
    def test_get_stats_for_patch(self):
        """Test that get_stats_for_patch returns the correct queryset."""
        stats = ChampionStatsPatch.get_stats_for_patch(self.patch)
        self.assertEqual(stats.count(), 2)
        self.assertIn(self.stats1, stats)
        self.assertIn(self.stats2, stats)
        
        # Test with non-existent patch
        stats = ChampionStatsPatch.get_stats_for_patch('99.99')
        self.assertEqual(stats.count(), 0)
    
    def test_update_stats(self):
        """Test that update_stats correctly updates the statistics."""
        summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='TestPlayer',
            tag_line='NA1'
        )
        
        participant = Participant.objects.create(
            match=self.match1,
            summoner=summoner,
            champion=self.champion1,
            kills=5,
            deaths=3,
            assists=10,
            creep_score=50,
            team=100,
            win=True,
            game_name='TestPlayer'
        )
        
        # Initial values
        initial_played = self.stats1.total_played
        initial_wins = self.stats1.total_wins
        
        # Update stats
        self.stats1.update_stats(participant)
        
        # Verify updates
        self.assertEqual(self.stats1.total_played, initial_played + 1)
        self.assertEqual(self.stats1.total_wins, initial_wins + 1)
        
        # Test with losing participant
        participant.win = False
        initial_losses = self.stats1.total_losses
        self.stats1.update_stats(participant)
        self.assertEqual(self.stats1.total_losses, initial_losses + 1)
