from django.test import TestCase, Client
from django.urls import reverse
from match_history.models import Match, Participant, Summoner, Champion
import datetime

class MatchDetailsPanelTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
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
            game_mode='ARAM',
            game_version='13.15.1'
        )
        
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            win=True,
            total_damage_dealt_to_champions=15000,
            physical_damage_dealt_to_champions=10000,
            magic_damage_dealt_to_champions=4000,
            true_damage_dealt_to_champions=1000,
            total_damage_taken=12000,
            total_heal=5000,
            gold_earned=12000,
            gold_spent=11000,
            vision_score=10,
            time_ccing_others=15,
            largest_killing_spree=3
        )
        
        self.client = Client()
    
    def test_match_details_panel_html_structure(self):
        """Test that the match details panel HTML structure is correctly rendered"""
        # Assuming there's a view that renders the match list
        response = self.client.get(reverse('match_history:summoner_detail', args=[self.summoner.game_name, self.summoner.tag_line]))
        
        # Check that the response contains the match details panel elements
        self.assertContains(response, 'match-details-panel')
        self.assertContains(response, 'match-details-content')
        self.assertContains(response, 'details-section')
        
        # Check for specific sections
        self.assertContains(response, 'Detailed Statistics')
        self.assertContains(response, 'Gold & Economy')
        self.assertContains(response, 'Combat Stats')
        
        # Check for specific stats
        self.assertContains(response, 'Total Damage:')
        self.assertContains(response, 'Gold Earned:')
        self.assertContains(response, 'Physical Damage:')
    
    def test_match_card_has_data_match_id(self):
        """Test that each match card has a data-match-id attribute"""
        response = self.client.get(reverse('match_history:summoner_detail', args=[self.summoner.game_name, self.summoner.tag_line]))
        
        # Check that the match card has the data-match-id attribute
        self.assertContains(response, f'data-match-id="{self.match.id}"')