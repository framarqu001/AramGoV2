from django.test import TestCase, Client
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from django.urls import reverse
from .models import Champion, Match, ChampionStatsPatch
import datetime


class ChampionStatsViewTest(TestCase):
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
            match_id='match_003',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version=f'{self.patch}.1',
            winner=100
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
        
        # Create client
        self.client = Client()
        
        # Clear cache
        cache.clear()
    
    @patch('match_history.views._get_champion_stats_for_patch')
    def test_champions_view(self, mock_get_stats):
        """Test that champions view correctly renders with stats."""
        # Mock the helper function
        mock_get_stats.return_value = [
            (self.champion1, {
                'patch': self.patch,
                'total_played': 100,
                'total_wins': 60,
                'total_losses': 40,
                'win_rate': 60.0,
                'pick_rate': 50.0
            }),
            (self.champion2, {
                'patch': self.patch,
                'total_played': 80,
                'total_wins': 30,
                'total_losses': 50,
                'win_rate': 37.5,
                'pick_rate': 40.0
            })
        ]
        
        # Get the champions page
        response = self.client.get(reverse('match_history:champions'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'match_history/champions.html')
        
        # Check context
        self.assertEqual(response.context['current_patch'], self.patch)
        self.assertEqual(len(response.context['champion_query']), 2)
        
        # Verify helper function was called
        mock_get_stats.assert_called_once()
    
    @patch('match_history.views._get_champion_stats_for_patch')
    def test_champions_view_with_invalid_patch(self, mock_get_stats):
        """Test that champions view handles invalid patch values."""
        # Mock the helper function to return None (invalid patch)
        mock_get_stats.return_value = None
        
        # Get the champions page with invalid patch
        response = self.client.get(reverse('match_history:champions') + '?patch=invalid')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'match_history/champions.html')
        
        # Check error message
        self.assertIn('error', response.context)
        
        # Verify helper function was called twice (once for requested patch, once for default)
        self.assertEqual(mock_get_stats.call_count, 2)
    
    @patch('match_history.views.cache.get')
    @patch('match_history.views.cache.set')
    def test_get_champion_stats_for_patch_caching(self, mock_cache_set, mock_cache_get):
        """Test that _get_champion_stats_for_patch correctly uses caching."""
        from match_history.views import _get_champion_stats_for_patch
        
        # Mock cache miss
        mock_cache_get.return_value = None
        
        # Call the function
        stats = _get_champion_stats_for_patch(self.patch)
        
        # Verify cache was set
        mock_cache_set.assert_called_once()
        
        # Mock cache hit
        cached_data = [
            (self.champion1, {
                'patch': self.patch,
                'total_played': 100,
                'total_wins': 60,
                'total_losses': 40,
                'win_rate': 60.0,
                'pick_rate': 50.0
            })
        ]
        mock_cache_get.return_value = cached_data
        
        # Call the function again
        stats = _get_champion_stats_for_patch(self.patch)
        
        # Verify result is from cache
        self.assertEqual(stats, cached_data)