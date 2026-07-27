import json
from django.test import TestCase, Client
from django.urls import reverse
from match_history.models import Match, Summoner, Champion, Participant, SummonerSpell, Rune, Item, ProfileIcon


class ExpandedMatchDataTest(TestCase):
    def setUp(self):
        # Create test data
        self.client = Client()
        
        # Create a profile icon
        self.profile_icon = ProfileIcon.objects.create(
            profile_id='1',
            image_path='1.png'
        )
        
        # Create a summoner
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='TestPlayer',
            tag_line='NA1',
            normalized_game_name='testplayer',
            normalized_tag_line='na1',
            summoner_level=100,
            profile_icon=self.profile_icon
        )
        
        # Create a champion
        self.champion = Champion.objects.create(
            champion_id='1',
            name='TestChamp',
            title='The Test Champion',
            image_path='TestChamp.png',
            splash_image_path='TestChamp_0.jpg'
        )
        
        # Create summoner spells
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name='Ignite',
            image_path='SummonerIgnite.png'
        )
        
        # Create runes
        self.rune1 = Rune.objects.create(
            rune_id=1,
            name='Conqueror',
            image_path='Conqueror.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=2,
            name='Triumph',
            image_path='Triumph.png'
        )
        
        # Create items
        self.item1 = Item.objects.create(
            item_id='1',
            name='Doran\'s Blade',
            image_path='1.png'
        )
        
        self.item2 = Item.objects.create(
            item_id='2',
            name='Health Potion',
            image_path='2.png'
        )
        
        # Create a match
        self.match = Match.objects.create(
            match_id='TEST123',
            game_start='2023-01-01T12:00:00Z',
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='14.1.1',
            winner=100  # Blue team wins
        )
        
        # Create a participant
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
            creep_score=100,
            item1=self.item1,
            item2=self.item2,
            team=100,  # Blue team
            win=True,
            game_name='TestPlayer'
        )

    def test_expanded_match_data_field_exists(self):
        """Test that the expanded_match_data field exists on the Match model"""
        self.assertTrue(hasattr(self.match, 'expanded_match_data'))
        
    def test_get_expanded_match_data_method(self):
        """Test the get_expanded_match_data method"""
        # Initially, expanded_match_data should be None
        self.assertIsNone(self.match.expanded_match_data)
        
        # Call the method to generate expanded data
        expanded_data = self.match.get_expanded_match_data()
        
        # Verify the expanded data structure
        self.assertEqual(expanded_data['match_id'], self.match.match_id)
        self.assertEqual(expanded_data['game_mode'], self.match.game_mode)
        self.assertEqual(expanded_data['patch'], self.match.get_patch())
        
        # Verify blue team data
        self.assertTrue(expanded_data['blue_team']['win'])
        self.assertEqual(len(expanded_data['blue_team']['participants']), 1)
        
        # Verify participant data
        participant_data = expanded_data['blue_team']['participants'][0]
        self.assertEqual(participant_data['summoner_name'], self.participant.game_name)
        self.assertEqual(participant_data['champion_name'], self.champion.name)
        self.assertEqual(participant_data['kills'], self.participant.kills)
        self.assertEqual(participant_data['deaths'], self.participant.deaths)
        self.assertEqual(participant_data['assists'], self.participant.assists)
        
        # After calling get_expanded_match_data, the field should be populated
        self.match.refresh_from_db()
        self.assertIsNotNone(self.match.expanded_match_data)
        
    def test_expanded_match_data_endpoint(self):
        """Test the API endpoint for expanded match data"""
        url = reverse('match_history:expanded_match_data', args=[self.match.match_id])
        
        # Make request with AJAX header
        response = self.client.get(
            url, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['match_id'], self.match.match_id)
        self.assertIn('expanded_data', data)
        
        # Verify expanded data content
        expanded_data = data['expanded_data']
        self.assertEqual(expanded_data['match_id'], self.match.match_id)
        self.assertEqual(expanded_data['game_mode'], self.match.game_mode)
        
    def test_expanded_match_data_caching(self):
        """Test that expanded match data is cached properly"""
        # First call should generate the data
        expanded_data1 = self.match.get_expanded_match_data()
        
        # Modify some data that would affect the expanded data if regenerated
        self.participant.kills = 20
        self.participant.save()
        
        # Second call should return cached data
        expanded_data2 = self.match.get_expanded_match_data()
        
        # The cached data should match the first call, not reflect the updated kills
        self.assertEqual(expanded_data1, expanded_data2)
        self.assertEqual(expanded_data2['blue_team']['participants'][0]['kills'], 10)  # Original value