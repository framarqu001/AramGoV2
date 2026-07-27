from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from match_history.models import Match, Participant, Summoner, Champion, SummonerSpell, Rune
from django.utils import timezone
import datetime


class ExtendedMatchStatsTest(TestCase):
    def setUp(self):
        # Create test data
        self.champion = Champion.objects.create(
            champion_id="1",
            name="Test Champion",
            title="Test Title",
            image_path="test.png",
            splash_image_path="test_splash.png"
        )
        
        self.spell = SummonerSpell.objects.create(
            spell_id=1,
            name="Test Spell",
            image_path="test_spell.png"
        )
        
        self.rune = Rune.objects.create(
            rune_id=1,
            name="Test Rune",
            image_path="test_rune.png"
        )
        
        self.summoner = Summoner.objects.create(
            puuid="test_puuid",
            game_name="TestPlayer",
            normalized_game_name="testplayer",
            tag_line="TEST",
            normalized_tag_line="test"
        )
        
        self.match = Match.objects.create(
            match_id="TEST123",
            game_start=timezone.now() - datetime.timedelta(days=1),
            game_duration=1200,  # 20 minutes
            game_mode="ARAM",
            game_version="14.17.1",
            winner=Match.BLUE_TEAM,
            blue_team_towers=5,
            red_team_towers=2,
            blue_team_dragons=2,
            red_team_dragons=1,
            blue_team_barons=1,
            red_team_barons=0,
            blue_team_heralds=0,
            red_team_heralds=0
        )
        
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            spell1=self.spell,
            spell2=self.spell,
            rune1=self.rune,
            rune2=self.rune,
            creep_score=100,
            team=Match.BLUE_TEAM,
            win=True,
            game_name="TestPlayer",
            total_damage_dealt=15000,
            physical_damage_dealt=10000,
            magic_damage_dealt=4000,
            true_damage_dealt=1000,
            total_damage_taken=8000,
            gold_earned=12000,
            gold_spent=11000,
            vision_score=20,
            wards_placed=5,
            wards_killed=3
        )
        
    def test_match_objective_stats(self):
        """Test that match objective statistics are correctly stored and retrieved"""
        self.assertEqual(self.match.blue_team_towers, 5)
        self.assertEqual(self.match.red_team_towers, 2)
        self.assertEqual(self.match.blue_team_dragons, 2)
        self.assertEqual(self.match.red_team_dragons, 1)
        self.assertEqual(self.match.blue_team_barons, 1)
        self.assertEqual(self.match.red_team_barons, 0)
        
        # Test the get_team_objectives method
        blue_objectives = self.match.get_team_objectives(Match.BLUE_TEAM)
        self.assertEqual(blue_objectives['towers'], 5)
        self.assertEqual(blue_objectives['dragons'], 2)
        self.assertEqual(blue_objectives['barons'], 1)
        self.assertEqual(blue_objectives['heralds'], 0)
        
        red_objectives = self.match.get_team_objectives(Match.RED_TEAM)
        self.assertEqual(red_objectives['towers'], 2)
        self.assertEqual(red_objectives['dragons'], 1)
        self.assertEqual(red_objectives['barons'], 0)
        self.assertEqual(red_objectives['heralds'], 0)
        
    def test_participant_damage_stats(self):
        """Test that participant damage statistics are correctly stored and retrieved"""
        self.assertEqual(self.participant.total_damage_dealt, 15000)
        self.assertEqual(self.participant.physical_damage_dealt, 10000)
        self.assertEqual(self.participant.magic_damage_dealt, 4000)
        self.assertEqual(self.participant.true_damage_dealt, 1000)
        self.assertEqual(self.participant.total_damage_taken, 8000)
        
        # Test the get_damage_stats method
        damage_stats = self.participant.get_damage_stats()
        self.assertEqual(damage_stats['total_dealt'], 15000)
        self.assertEqual(damage_stats['physical_dealt'], 10000)
        self.assertEqual(damage_stats['magic_dealt'], 4000)
        self.assertEqual(damage_stats['true_dealt'], 1000)
        self.assertEqual(damage_stats['total_taken'], 8000)
        
    def test_participant_gold_stats(self):
        """Test that participant gold statistics are correctly stored and retrieved"""
        self.assertEqual(self.participant.gold_earned, 12000)
        self.assertEqual(self.participant.gold_spent, 11000)
        
        # Test the get_gold_stats method
        gold_stats = self.participant.get_gold_stats()
        self.assertEqual(gold_stats['earned'], 12000)
        self.assertEqual(gold_stats['spent'], 11000)
        self.assertEqual(gold_stats['efficiency'], "91.7%")
        
    def test_participant_vision_stats(self):
        """Test that participant vision statistics are correctly stored and retrieved"""
        self.assertEqual(self.participant.vision_score, 20)
        self.assertEqual(self.participant.wards_placed, 5)
        self.assertEqual(self.participant.wards_killed, 3)
        
        # Test the get_vision_stats method
        vision_stats = self.participant.get_vision_stats()
        self.assertEqual(vision_stats['score'], 20)
        self.assertEqual(vision_stats['wards_placed'], 5)
        self.assertEqual(vision_stats['wards_killed'], 3)
        
    def test_cache_implementation(self):
        """Test that match data is properly cached"""
        # Clear the cache first
        cache.clear()
        
        # Create a cache key
        cache_key = f'expanded_match_data_{self.match.match_id}_{self.summoner.puuid}'
        
        # Check that the cache is empty
        self.assertIsNone(cache.get(cache_key))
        
        # Create some test data to cache
        test_data = {
            'match': self.match,
            'participant': self.participant,
            'stats': {
                'damage': self.participant.get_damage_stats(),
                'gold': self.participant.get_gold_stats(),
                'vision': self.participant.get_vision_stats()
            }
        }
        
        # Cache the data
        cache.set(cache_key, test_data, timeout=3600)
        
        # Check that the data is in the cache
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['match'], self.match)
        self.assertEqual(cached_data['participant'], self.participant)
        
    def test_context_processor(self):
        """Test that the context processor provides expanded match data"""
        # This would typically be tested with a view test, but we can test the function directly
        from match_history.context_processors import expanded_match_data
        
        # Create a mock request with a match_id
        class MockRequest:
            def __init__(self):
                self.GET = {'match_id': 'TEST123'}
                
        request = MockRequest()
        
        # Clear the cache first
        cache.clear()
        
        # Call the context processor
        context = expanded_match_data(request)
        
        # Check that the context contains expanded match data
        self.assertIn('expanded_match_data', context)
        self.assertIsNotNone(context['expanded_match_data'])
        
        # Check that the match data is cached
        cache_key = f'expanded_match_data_context_TEST123'
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)