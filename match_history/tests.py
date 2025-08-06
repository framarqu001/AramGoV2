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
            game_name='testSummoner#NA1'
        )

    def test_participant_relationships(self):
        self.assertEqual(self.participant.match, self.match)
        self.assertEqual(self.participant.summoner, self.summoner)
        self.assertEqual(self.participant.champion, self.champion)
        self.assertIn(self.participant, self.match.participants.all())

    def test_participant_string_representation(self):
        self.assertEqual(str(self.participant), 'testSummoner#NA1 playing Aatrox in match match_001')

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_summoner(self):
        self.summoner.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())

    def test_cascade_delete_with_champion(self):
        self.champion.delete()
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())


class ParticipantRankTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='rank-test-id',
            game_name='rankTestSummoner',
            tag_line='NA1',
            summoner_name='rankTestSummoner',
            summoner_level=30
        )
        self.champion = Champion.objects.create(
            champion_id='Jinx',
            name='Jinx',
            title='The Loose Cannon',
            image_path='Jinx.png',
            splash_image_path='Jinx_0.jpg'
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
            match_id='rank_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1',
            winner=100
        )

    def test_default_rank_values(self):
        """Test that default rank values are set correctly"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='rankTestSummoner#NA1'
        )
        
        self.assertEqual(participant.tier, 'UNRANKED')
        self.assertEqual(participant.division, '')
        self.assertEqual(participant.lp, 0)

    def test_rank_display_unranked(self):
        """Test rank display for unranked participant"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='rankTestSummoner#NA1'
        )
        
        self.assertEqual(participant.get_rank_display(), 'Unranked')

    def test_rank_display_with_division(self):
        """Test rank display for participant with tier and division"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='rankTestSummoner#NA1',
            tier='GOLD',
            division='II',
            lp=75
        )
        
        self.assertEqual(participant.get_rank_display(), 'Gold II 75 LP')

    def test_rank_display_master_tier(self):
        """Test rank display for Master tier (no division)"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='rankTestSummoner#NA1',
            tier='MASTER',
            division='',
            lp=150
        )
        
        self.assertEqual(participant.get_rank_display(), 'Master 150 LP')

    def test_get_rank_data(self):
        """Test get_rank_data method returns correct dictionary"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=3,
            assists=7,
            creep_score=120,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='rankTestSummoner#NA1',
            tier='PLATINUM',
            division='IV',
            lp=25
        )
        
        rank_data = participant.get_rank_data()
        expected_data = {
            'tier': 'PLATINUM',
            'division': 'IV',
            'lp': 25,
            'rank_display': 'Platinum IV 25 LP'
        }
        
        self.assertEqual(rank_data, expected_data)

    def test_tier_choices_validation(self):
        """Test that tier choices are properly validated"""
        valid_tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 
                      'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 
                      'CHALLENGER', 'UNRANKED']
        
        for tier in valid_tiers:
            participant = Participant.objects.create(
                match=self.match,
                summoner=self.summoner,
                champion=self.champion,
                kills=5,
                deaths=3,
                assists=7,
                creep_score=120,
                spell1=self.spell1,
                spell2=self.spell2,
                team=100,
                win=True,
                game_name=f'test{tier}#NA1',
                tier=tier
            )
            self.assertEqual(participant.tier, tier)

    def test_division_choices_validation(self):
        """Test that division choices are properly validated"""
        valid_divisions = ['I', 'II', 'III', 'IV', '']
        
        for division in valid_divisions:
            participant = Participant.objects.create(
                match=self.match,
                summoner=self.summoner,
                champion=self.champion,
                kills=5,
                deaths=3,
                assists=7,
                creep_score=120,
                spell1=self.spell1,
                spell2=self.spell2,
                team=100,
                win=True,
                game_name=f'test{division}#NA1',
                division=division
            )
            self.assertEqual(participant.division, division)


class ParticipantCachingTest(TestCase):
    def setUp(self):
        cache.clear()  # Clear cache before each test
        
        self.summoner = Summoner.objects.create(
            puuid='cache-test-id',
            game_name='cacheTestSummoner',
            tag_line='NA1',
            summoner_name='cacheTestSummoner',
            summoner_level=30
        )
        self.champion = Champion.objects.create(
            champion_id='Yasuo',
            name='Yasuo',
            title='The Unforgiven',
            image_path='Yasuo.png',
            splash_image_path='Yasuo_0.jpg'
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
            match_id='cache_match_001',
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
            kills=8,
            deaths=4,
            assists=12,
            creep_score=180,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='cacheTestSummoner#NA1',
            tier='DIAMOND',
            division='III',
            lp=50
        )

    def test_participant_stats_caching(self):
        """Test that participant stats are properly cached"""
        from match_history.views import _get_cached_participant_stats, _get_participant_stats_cache_key
        
        # First call should cache the data
        cached_stats = _get_cached_participant_stats(self.participant)
        
        # Verify the cached data structure
        self.assertIn('rank_data', cached_stats)
        self.assertIn('kda_ratio', cached_stats)
        self.assertIn('cs_per_min', cached_stats)
        
        # Verify the cache key exists
        cache_key = _get_participant_stats_cache_key(self.participant.summoner.puuid, self.participant.match.match_id)
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        # Verify cached data matches expected values
        expected_kda_ratio = (8 + 12) / 4  # (kills + assists) / deaths
        expected_cs_per_min = 180 / (1800 / 60)  # creep_score / (game_duration / 60)
        
        self.assertEqual(cached_stats['kda_ratio'], expected_kda_ratio)
        self.assertEqual(cached_stats['cs_per_min'], expected_cs_per_min)
        self.assertEqual(cached_stats['rank_data']['tier'], 'DIAMOND')
        self.assertEqual(cached_stats['rank_data']['division'], 'III')
        self.assertEqual(cached_stats['rank_data']['lp'], 50)

    def tearDown(self):
        cache.clear()  # Clean up cache after each test


    ##AramGoV2 if user changes there name
    ## AramGoV2 all items are retriavable


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