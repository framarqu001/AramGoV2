from django.test import TestCase, Client
from django.urls import reverse
from match_history.models import Participant, Match, Summoner, Champion, SummonerSpell, Rune
from datetime import datetime
from django.utils import timezone


class PlayerStatsTest(TestCase):
    def setUp(self):
        # Create test data
        self.champion = Champion.objects.create(
            champion_id="1",
            name="Test Champion",
            title="Test Title",
            image_path="test.png",
            splash_image_path="test_splash.png"
        )
        
        self.summoner = Summoner.objects.create(
            puuid="test_puuid",
            game_name="TestSummoner",
            normalized_game_name="testsummoner",
            tag_line="TEST",
            normalized_tag_line="test"
        )
        
        self.match = Match.objects.create(
            match_id="TEST123",
            game_start=timezone.now(),
            game_duration=1200,  # 20 minutes
            game_mode="ARAM",
            game_version="14.17.1",
            winner=100
        )
        
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name="Test Spell 1",
            image_path="test_spell1.png"
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name="Test Spell 2",
            image_path="test_spell2.png"
        )
        
        self.rune1 = Rune.objects.create(
            rune_id=1,
            name="Test Rune 1",
            image_path="test_rune1.png"
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=2,
            name="Test Rune 2",
            image_path="test_rune2.png"
        )
        
        # Create participant with the new stats fields
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
            damage_dealt=25000,
            gold_earned=12500,
            vision_score=20,
            team=100,
            win=True,
            game_name="TestSummoner"
        )
        
    def test_participant_has_new_fields(self):
        """Test that the Participant model has the new fields"""
        participant = Participant.objects.get(pk=self.participant.pk)
        self.assertEqual(participant.damage_dealt, 25000)
        self.assertEqual(participant.gold_earned, 12500)
        self.assertEqual(participant.vision_score, 20)
        
    def test_match_data_includes_new_stats(self):
        """Test that the _get_match_data function includes the new stats"""
        from match_history.views import _get_match_data
        
        # Create a mock page_obj that contains our match
        class MockPageObj:
            def __init__(self, matches):
                self.matches = matches
                
            def __iter__(self):
                return iter(self.matches)
        
        # Set up the match with all_participants attribute
        self.match.all_participants = [self.participant]
        page_obj = MockPageObj([self.match])
        
        # Call _get_match_data
        match_data = _get_match_data(self.summoner, page_obj)
        
        # Check that the new stats are included in main_stats
        _, _, _, _, main_stats = match_data[0]
        self.assertIn('damage_dealt', main_stats)
        self.assertIn('gold_earned', main_stats)
        self.assertIn('vision_score', main_stats)
        self.assertEqual(main_stats['damage_dealt'], '25,000')
        self.assertEqual(main_stats['gold_earned'], '12,500')
        self.assertEqual(main_stats['vision_score'], 20)