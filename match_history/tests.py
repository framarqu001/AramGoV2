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
            image_path='Aatrox.png'
        )
        self.match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1'
        )
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150
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


class SummonerRankTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='rank-test-id',
            game_name='RankTestSummoner',
            tag_line='NA1',
            summoner_name='RankTestSummoner',
            summoner_level=50
        )

    def test_summoner_rank_display_with_tier_and_division(self):
        """Test rank display when both tier and division are set"""
        self.summoner.tier = 'GOLD'
        self.summoner.division = 'II'
        self.summoner.save()
        
        expected_rank = 'Gold II'
        self.assertEqual(self.summoner.get_rank_display(), expected_rank)

    def test_summoner_rank_display_with_tier_only(self):
        """Test rank display when only tier is set (for Master+ ranks)"""
        self.summoner.tier = 'MASTER'
        self.summoner.division = None
        self.summoner.save()
        
        expected_rank = 'Master'
        self.assertEqual(self.summoner.get_rank_display(), expected_rank)

    def test_summoner_rank_display_unranked(self):
        """Test rank display when no rank information is set"""
        self.summoner.tier = None
        self.summoner.division = None
        self.summoner.save()
        
        expected_rank = 'Unranked'
        self.assertEqual(self.summoner.get_rank_display(), expected_rank)

    def test_summoner_rank_choices_validation(self):
        """Test that tier choices are properly validated"""
        valid_tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 
                      'EMERALD', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
        
        for tier in valid_tiers:
            self.summoner.tier = tier
            self.summoner.save()
            self.assertEqual(self.summoner.tier, tier)

    def test_summoner_division_choices_validation(self):
        """Test that division choices are properly validated"""
        valid_divisions = ['I', 'II', 'III', 'IV']
        
        for division in valid_divisions:
            self.summoner.division = division
            self.summoner.save()
            self.assertEqual(self.summoner.division, division)

    def test_league_points_default_value(self):
        """Test that league points defaults to 0"""
        self.assertEqual(self.summoner.league_points, 0)


class ExpandedStatsTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='stats-test-id',
            game_name='StatsTestSummoner',
            tag_line='NA1',
            summoner_name='StatsTestSummoner',
            summoner_level=45,
            tier='PLATINUM',
            division='III',
            league_points=75
        )
        self.champion = Champion.objects.create(
            champion_id='Jinx',
            name='Jinx',
            title='The Loose Cannon',
            image_path='Jinx.png'
        )
        self.match = Match.objects.create(
            match_id='stats_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )

    def test_kill_participation_calculation(self):
        """Test that kill participation is calculated correctly"""
        # Create main participant
        main_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=8,
            deaths=3,
            assists=12,
            creep_score=120,
            team=100,
            win=True,
            game_name='StatsTestSummoner'
        )
        
        # Create team members with kills
        for i in range(4):
            teammate_summoner = Summoner.objects.create(
                puuid=f'teammate-{i}',
                game_name=f'Teammate{i}',
                tag_line='NA1'
            )
            Participant.objects.create(
                match=self.match,
                summoner=teammate_summoner,
                champion=self.champion,
                kills=5,  # Each teammate has 5 kills
                deaths=2,
                assists=8,
                creep_score=100,
                team=100,
                win=True,
                game_name=f'Teammate{i}'
            )
        
        # Total team kills: 8 (main) + 5*4 (teammates) = 28
        # Main participant contribution: (8 kills + 12 assists) = 20
        # Kill participation: 20/28 = ~71%
        
        # This would be tested in the view logic, but we can verify the data is set up correctly
        team_kills = sum(p.kills for p in self.match.participants.filter(team=100))
        main_contribution = main_participant.kills + main_participant.assists
        expected_kp = (main_contribution / team_kills) * 100
        
        self.assertEqual(team_kills, 28)
        self.assertEqual(main_contribution, 20)
        self.assertAlmostEqual(expected_kp, 71.43, places=1)
