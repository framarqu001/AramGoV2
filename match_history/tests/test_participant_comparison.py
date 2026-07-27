from django.test import TestCase
from match_history.models import Participant, Match, Champion, Summoner, SummonerSpell


class ParticipantComparisonTests(TestCase):
    def setUp(self):
        # Create test data
        self.match = Match.objects.create(
            match_id="TEST123",
            game_start="2024-01-01T12:00:00Z",
            game_duration=1200,  # 20 minutes
            game_mode="ARAM",
            game_version="14.17.1",
            winner=100
        )
        
        self.champion1 = Champion.objects.create(
            champion_id="1",
            name="TestChamp1",
            title="Test Champion 1",
            image_path="test1.png",
            splash_image_path="test1_splash.jpg"
        )
        
        self.champion2 = Champion.objects.create(
            champion_id="2",
            name="TestChamp2",
            title="Test Champion 2",
            image_path="test2.png",
            splash_image_path="test2_splash.jpg"
        )
        
        self.summoner1 = Summoner.objects.create(
            puuid="PUUID1",
            game_name="TestPlayer1",
            tag_line="NA1"
        )
        
        self.summoner2 = Summoner.objects.create(
            puuid="PUUID2",
            game_name="TestPlayer2",
            tag_line="NA1"
        )
        
        self.spell = SummonerSpell.objects.create(
            spell_id=1,
            name="Test Spell",
            image_path="test_spell.png"
        )
        
        # Create participants with different stats
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=10,
            deaths=5,
            assists=8,
            spell1=self.spell,
            spell2=self.spell,
            creep_score=100,
            team=100,  # Blue team
            win=True,
            game_name="TestPlayer1",
            role=Participant.MAGE
        )
        
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=7,
            deaths=8,
            assists=6,
            spell1=self.spell,
            spell2=self.spell,
            creep_score=80,
            team=200,  # Red team
            win=False,
            game_name="TestPlayer2",
            role=Participant.MAGE
        )
    
    def test_get_kda(self):
        """Test KDA calculation"""
        # (10 + 8) / 5 = 3.6
        self.assertEqual(self.participant1.get_kda(), 3.6)
        # (7 + 6) / 8 = 1.625
        self.assertEqual(self.participant2.get_kda(), 1.625)
    
    def test_get_cs_per_min(self):
        """Test CS per minute calculation"""
        # 100 / (1200 / 60) = 100 / 20 = 5
        self.assertEqual(self.participant1.get_cs_per_min(self.match.game_duration), 5)
        # 80 / (1200 / 60) = 80 / 20 = 4
        self.assertEqual(self.participant2.get_cs_per_min(self.match.game_duration), 4)
    
    def test_compare_stats(self):
        """Test stat comparison between participants"""
        comparison = self.participant1.compare_stats(self.participant2)
        
        self.assertEqual(comparison['kills_diff'], 3)  # 10 - 7
        self.assertEqual(comparison['deaths_diff'], -3)  # 5 - 8
        self.assertEqual(comparison['assists_diff'], 2)  # 8 - 6
        self.assertEqual(comparison['cs_diff'], 20)  # 100 - 80
        self.assertEqual(comparison['kda_diff'], 1.975)  # 3.6 - 1.625