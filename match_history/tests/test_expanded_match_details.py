from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse
import json
import datetime

from match_history.models import (
    Summoner, Champion, Match, Participant, 
    SummonerSpell, Rune, Item, ProfileIcon
)


class ExpandedMatchDetailsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.profile_icon = ProfileIcon.objects.create(
            profile_id='1',
            image_path='1.png'
        )
        
        self.summoner = Summoner.objects.create(
            puuid='test-summoner-id',
            game_name='TestPlayer',
            tag_line='NA1',
            normalized_game_name='testplayer',
            normalized_tag_line='na1',
            profile_icon=self.profile_icon
        )
        
        self.champion = Champion.objects.create(
            champion_id='TestChamp',
            name='Test Champion',
            title='The Test',
            image_path='test.png',
            splash_image_path='test_splash.jpg'
        )
        
        self.match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1500,  # 25 minutes
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100  # Blue team wins
        )
        
        # Create spell and rune objects for participants
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name='Flash',
            image_path='flash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name='Ignite',
            image_path='ignite.png'
        )
        
        self.rune1 = Rune.objects.create(
            rune_id=1,
            name='Conqueror',
            image_path='conqueror.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=2,
            name='Triumph',
            image_path='triumph.png'
        )
        
        # Create items
        self.item1 = Item.objects.create(
            item_id='1001',
            name='Boots',
            image_path='boots.png'
        )
        
        # Create participants for the match
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=50,
            team=100,  # Blue team
            win=True,
            game_name='TestPlayer',
            item1=self.item1
        )
    
    def test_expanded_match_details_endpoint(self):
        # Test the expanded match details endpoint
        url = reverse('match_history:match_details', args=[self.match.match_id])
        response = self.client.get(url)
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains the expected data
        self.assertIn('match_details', data)
        match_details = data['match_details']
        
        # Check match details
        self.assertEqual(match_details['match_id'], self.match.match_id)
        self.assertEqual(match_details['game_mode'], 'ARAM')
        self.assertEqual(match_details['winner'], 100)
        
        # Check that blue team contains our participant
        self.assertTrue(len(match_details['blue_team']) > 0)
        
        # Find our participant in the blue team
        participant_found = False
        for player in match_details['blue_team']:
            if player['summoner_name'] == 'TestPlayer':
                participant_found = True
                self.assertEqual(player['kills'], 10)
                self.assertEqual(player['deaths'], 5)
                self.assertEqual(player['assists'], 15)
                break
        
        self.assertTrue(participant_found, "Participant not found in the response")
    
    def test_expanded_match_details_caching(self):
        # Test that the endpoint uses caching
        url = reverse('match_history:match_details', args=[self.match.match_id])
        
        # Clear the cache first
        cache_key = f'expanded_match_{self.match.match_id}'
        cache.delete(cache_key)
        
        # First request should hit the database
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        
        # Modify the match to verify cache is being used
        self.match.game_mode = 'MODIFIED'
        self.match.save()
        
        # Second request should use the cache and return the original data
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        
        # Parse the responses
        data1 = json.loads(response1.content)
        data2 = json.loads(response2.content)
        
        # The game mode should still be the original value due to caching
        self.assertEqual(data2['match_details']['game_mode'], 'ARAM')
        
        # Clear cache and verify we get the updated value
        cache.delete(cache_key)
        response3 = self.client.get(url)
        data3 = json.loads(response3.content)
        self.assertEqual(data3['match_details']['game_mode'], 'MODIFIED')