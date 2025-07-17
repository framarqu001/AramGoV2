import json
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from match_history.models import Match, Summoner, Participant, Champion
import datetime


class MatchCardOptimizationTests(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='testPlayer',
            tag_line='NA1',
            normalized_game_name='testplayer',
            normalized_tag_line='na1',
            summoner_name='testPlayer',
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
            game_creation=datetime.datetime.now(),
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1'
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
            damage_dealt=15000,
            damage_taken=10000,
            gold_earned=12000,
            vision_score=10
        )
        
        self.client = Client()
        
        # Clear cache before tests
        cache.clear()

    def test_match_details_endpoint(self):
        """Test that the match details endpoint returns correct data"""
        url = reverse('match_history:match_details', args=[self.match.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Check basic match data
        self.assertEqual(data['match_id'], self.match.id)
        self.assertEqual(data['game_duration'], self.match.game_duration)
        
        # Check team data
        self.assertEqual(len(data['blue_team']), 1)  # We only created one participant
        self.assertEqual(data['blue_team'][0]['summoner_name'], self.participant.game_name)
        self.assertEqual(data['blue_team'][0]['kills'], self.participant.kills)
        
    def test_match_details_caching(self):
        """Test that match details are properly cached"""
        url = reverse('match_history:match_details', args=[self.match.id])
        
        # First request should hit the database
        with self.assertNumQueries(lambda x: x > 0):
            response1 = self.client.get(url)
            self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache and not hit the database
        with self.assertNumQueries(0):
            response2 = self.client.get(url)
            self.assertEqual(response2.status_code, 200)
            
        # Both responses should have the same content
        self.assertEqual(response1.content, response2.content)
        
    def test_match_queryset_caching(self):
        """Test that match queryset is properly cached"""
        from match_history.views import _get_match_queryset
        
        # First call should hit the database
        with self.assertNumQueries(lambda x: x > 0):
            queryset1 = _get_match_queryset(self.summoner)
            
        # Second call should use cache
        with self.assertNumQueries(0):
            queryset2 = _get_match_queryset(self.summoner)
            
        # Both querysets should have the same matches
        self.assertEqual(list(queryset1), list(queryset2))