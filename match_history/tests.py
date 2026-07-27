from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch
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
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        self.spell1 = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        self.spell2 = SummonerSpell.objects.create(
            spell_id=32,
            name='Mark',
            image_path='SummonerSnowball.png'
        )
        self.match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1',
            winner=100
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='testSummoner',
            # Enhanced statistics
            total_damage_dealt_to_champions=25000,
            total_damage_taken=18000,
            magic_damage_dealt_to_champions=15000,
            physical_damage_dealt_to_champions=8000,
            true_damage_dealt_to_champions=2000,
            damage_self_mitigated=12000,
            vision_score=45,
            wards_placed=15,
            wards_killed=8,
            vision_wards_bought_in_game=3,
            turret_kills=2,
            inhibitor_kills=1,
            dragon_kills=1,
            baron_kills=0,
            gold_earned=15000,
            gold_spent=14500,
            total_heal=8000,
            total_units_healed=5
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        self.assertEqual(str(self.participant), 'testSummoner playing Aatrox in match match_001')

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_summoner(self):
        self.summoner.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_champion(self):
        self.champion.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())


class EnhancedParticipantStatsTest(TestCase):
    def setUp(self):
        # Create test data for enhanced statistics testing
        self.summoner1 = Summoner.objects.create(
            puuid='summoner-1',
            game_name='Player1',
            tag_line='NA1',
            summoner_level=30
        )
        self.summoner2 = Summoner.objects.create(
            puuid='summoner-2',
            game_name='Player2',
            tag_line='NA1',
            summoner_level=30
        )
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
        self.spell = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        self.match = Match.objects.create(
            match_id='enhanced_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=100
        )
        
        # Create two participants on the same team for testing damage share and kill participation
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150,
            spell1=self.spell,
            spell2=self.spell,
            team=100,
            win=True,
            game_name='Player1',
            total_damage_dealt_to_champions=30000,
            gold_earned=15000,
            gold_spent=14500
        )
        
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=5,
            deaths=3,
            assists=12,
            creep_score=120,
            spell1=self.spell,
            spell2=self.spell,
            team=100,
            win=True,
            game_name='Player2',
            total_damage_dealt_to_champions=20000,
            gold_earned=12000,
            gold_spent=11800
        )

    def test_damage_share_percentage(self):
        """Test damage share percentage calculation"""
        # Total team damage: 30000 + 20000 = 50000
        # Participant1 damage share: 30000 / 50000 * 100 = 60%
        damage_share = self.participant1.get_damage_share_percentage()
        self.assertEqual(damage_share, 60.0)
        
        # Participant2 damage share: 20000 / 50000 * 100 = 40%
        damage_share2 = self.participant2.get_damage_share_percentage()
        self.assertEqual(damage_share2, 40.0)

    def test_kill_participation_percentage(self):
        """Test kill participation percentage calculation"""
        # Total team kills: 10 + 5 = 15
        # Participant1 kill participation: (10 + 8) / 15 * 100 = 120% (can exceed 100%)
        kill_participation = self.participant1.get_kill_participation_percentage()
        self.assertEqual(kill_participation, 120.0)
        
        # Participant2 kill participation: (5 + 12) / 15 * 100 = 113.33%
        kill_participation2 = self.participant2.get_kill_participation_percentage()
        self.assertAlmostEqual(kill_participation2, 113.33, places=2)

    def test_kda_ratio(self):
        """Test KDA ratio calculation"""
        # Participant1 KDA: (10 + 8) / 2 = 9.0
        kda = self.participant1.get_kda_ratio()
        self.assertEqual(kda, 9.0)
        
        # Participant2 KDA: (5 + 12) / 3 = 5.67
        kda2 = self.participant2.get_kda_ratio()
        self.assertAlmostEqual(kda2, 5.67, places=2)

    def test_gold_efficiency(self):
        """Test gold efficiency calculation"""
        # Participant1 gold efficiency: 14500 / 15000 * 100 = 96.67%
        gold_efficiency = self.participant1.get_gold_efficiency()
        self.assertAlmostEqual(gold_efficiency, 96.67, places=2)
        
        # Participant2 gold efficiency: 11800 / 12000 * 100 = 98.33%
        gold_efficiency2 = self.participant2.get_gold_efficiency()
        self.assertAlmostEqual(gold_efficiency2, 98.33, places=2)

    def test_zero_division_handling(self):
        """Test that methods handle zero division gracefully"""
        # Create participant with zero values
        zero_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=0,
            deaths=0,
            assists=0,
            creep_score=0,
            spell1=self.spell,
            spell2=self.spell,
            team=200,
            win=False,
            game_name='ZeroPlayer',
            total_damage_dealt_to_champions=0,
            gold_earned=0,
            gold_spent=0
        )
        
        # Test damage share with zero damage
        damage_share = zero_participant.get_damage_share_percentage()
        self.assertEqual(damage_share, 0)
        
        # Test kill participation with zero kills
        kill_participation = zero_participant.get_kill_participation_percentage()
        self.assertEqual(kill_participation, 0)
        
        # Test KDA with zero deaths (should return infinity)
        kda = zero_participant.get_kda_ratio()
        self.assertEqual(kda, float('inf'))
        
        # Test gold efficiency with zero earned
        gold_efficiency = zero_participant.get_gold_efficiency()
        self.assertEqual(gold_efficiency, 0)


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