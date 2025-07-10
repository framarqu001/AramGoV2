"""
Tests for the Riot API client.
"""
import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings
from riotwatcher import ApiError

from AramGoV2.util.riot_api import RiotAPIClient


class RiotAPIClientTestCase(TestCase):
    """Test cases for the RiotAPIClient class."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure we have a test API key
        settings.RIOT_API_KEY = 'test_api_key'
        self.client = RiotAPIClient(region='na')
    
    @patch('AramGoV2.util.riot_api.RiotWatcher')
    @patch('AramGoV2.util.riot_api.LolWatcher')
    def test_initialization(self, mock_lol_watcher, mock_riot_watcher):
        """Test client initialization."""
        client = RiotAPIClient(region='na')
        
        self.assertEqual(client.region, 'na')
        self.assertEqual(client.platform, 'na1')
        self.assertEqual(client.regional_route, 'americas')
        
        mock_lol_watcher.assert_called_once_with('test_api_key')
        mock_riot_watcher.assert_called_once_with('test_api_key')
    
    @patch('AramGoV2.util.riot_api.cache')
    def test_get_summoner_by_riot_id_cache_hit(self, mock_cache):
        """Test getting summoner by Riot ID with cache hit."""
        # Mock cache hit
        mock_cache.get.return_value = {'id': 'test_id', 'name': 'TestSummoner'}
        
        result = self.client.get_summoner_by_riot_id('TestName', 'NA1')
        
        self.assertEqual(result, {'id': 'test_id', 'name': 'TestSummoner'})
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
    
    @patch('AramGoV2.util.riot_api.cache')
    def test_get_summoner_by_riot_id_cache_miss(self, mock_cache):
        """Test getting summoner by Riot ID with cache miss."""
        # Mock cache miss
        mock_cache.get.return_value = None
        
        # Mock API responses
        self.client.riot_watcher = MagicMock()
        self.client.lol_watcher = MagicMock()
        
        account_info = {'puuid': 'test_puuid', 'gameName': 'TestName', 'tagLine': 'NA1'}
        summoner_info = {'id': 'test_id', 'name': 'TestSummoner', 'puuid': 'test_puuid'}
        
        self.client.riot_watcher.account.by_riot_id.return_value = account_info
        self.client.lol_watcher.summoner.by_puuid.return_value = summoner_info
        
        result = self.client.get_summoner_by_riot_id('TestName', 'NA1')
        
        expected_result = {
            'id': 'test_id', 
            'name': 'TestSummoner', 
            'puuid': 'test_puuid',
            'gameName': 'TestName',
            'tagLine': 'NA1'
        }
        
        self.assertEqual(result, expected_result)
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        
        self.client.riot_watcher.account.by_riot_id.assert_called_once_with(
            'americas', 'TestName', 'NA1'
        )
        self.client.lol_watcher.summoner.by_puuid.assert_called_once_with(
            'na1', 'test_puuid'
        )
    
    @patch('AramGoV2.util.riot_api.cache')
    def test_get_match_list(self, mock_cache):
        """Test getting match list."""
        # Mock cache miss
        mock_cache.get.return_value = None
        
        # Mock API response
        self.client.lol_watcher = MagicMock()
        match_list = ['match1', 'match2', 'match3']
        self.client.lol_watcher.match.matchlist_by_puuid.return_value = match_list
        
        result = self.client.get_match_list('test_puuid')
        
        self.assertEqual(result, match_list)
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        
        self.client.lol_watcher.match.matchlist_by_puuid.assert_called_once_with(
            'americas', 'test_puuid', queue=450, count=20, start=0
        )
    
    @patch('AramGoV2.util.riot_api.cache')
    def test_get_match_details(self, mock_cache):
        """Test getting match details."""
        # Mock cache miss
        mock_cache.get.return_value = None
        
        # Mock API response
        self.client.lol_watcher = MagicMock()
        match_details = {'gameId': 'match1', 'participants': []}
        self.client.lol_watcher.match.by_id.return_value = match_details
        
        result = self.client.get_match_details('match1')
        
        self.assertEqual(result, match_details)
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()
        
        self.client.lol_watcher.match.by_id.assert_called_once_with(
            'americas', 'match1'
        )
    
    @patch('AramGoV2.util.riot_api.RiotAPIClient.get_match_list')
    @patch('AramGoV2.util.riot_api.time.sleep')
    def test_get_all_matches(self, mock_sleep, mock_get_match_list):
        """Test getting all matches."""
        # Mock first call returns full list (100 items)
        mock_get_match_list.side_effect = [
            ['match' + str(i) for i in range(100)],  # First call returns 100 matches
            ['match' + str(i) for i in range(100, 150)]  # Second call returns 50 matches
        ]
        
        result = self.client.get_all_matches('test_puuid')
        
        # Should have 150 matches total
        self.assertEqual(len(result), 150)
        self.assertEqual(mock_get_match_list.call_count, 2)
        mock_sleep.assert_called_once()
    
    @patch('AramGoV2.util.riot_api.logger')
    def test_handle_api_error_rate_limit(self, mock_logger):
        """Test handling rate limit API error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '30'}
        
        error = ApiError(mock_response)
        
        self.client._handle_api_error(error, "Test message")
        
        mock_logger.warning.assert_called_once()
    
    @patch('AramGoV2.util.riot_api.logger')
    def test_handle_api_error_not_found(self, mock_logger):
        """Test handling not found API error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        error = ApiError(mock_response)
        
        self.client._handle_api_error(error, "Test message")
        
        mock_logger.info.assert_called_once()


if __name__ == '__main__':
    unittest.main()