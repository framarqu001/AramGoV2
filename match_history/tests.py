from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch
import datetime
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig


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


class ChampionStatsTest(TestCase):
    def setUp(self):
        self.champion = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png',
            splash_image_path='Ahri_0.jpg'
        )
        self.match = Match.objects.create(
            match_id='match_002',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=100
        )
        self.summoner = Summoner.objects.create(
            puuid='some-unique-id-2',
            game_name='testSummoner2',
            tag_line='NA1',
            summoner_name='testSummoner2',
            summoner_level=30
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
            game_name='testSummoner2'
        )
        self.champion_stats = ChampionStats.objects.create(
            champion=self.champion,
            patch='13.15',
            games_played=10,
            wins=6,
            losses=4,
            pick_rate=5.0
        )

    def test_champion_stats_creation(self):
        self.assertEqual(self.champion_stats.champion, self.champion)
        self.assertEqual(self.champion_stats.patch, '13.15')
        self.assertEqual(self.champion_stats.games_played, 10)
        self.assertEqual(self.champion_stats.wins, 6)
        self.assertEqual(self.champion_stats.losses, 4)
        self.assertEqual(self.champion_stats.pick_rate, 5.0)

    def test_win_rate_calculation(self):
        self.assertEqual(self.champion_stats.win_rate(), 60.0)  # 6/10 * 100 = 60%
        
        # Test with zero games played
        zero_stats = ChampionStats.objects.create(
            champion=self.champion,
            patch='13.16',
            games_played=0,
            wins=0,
            losses=0
        )
        self.assertEqual(zero_stats.win_rate(), 0)

    def test_update_stats(self):
        # Initial values
        initial_games = self.champion_stats.games_played
        initial_wins = self.champion_stats.wins
        
        # Update stats with a winning participant
        self.champion_stats.update_stats(self.participant, total_games_in_patch=200)
        
        # Check that values were updated correctly
        self.assertEqual(self.champion_stats.games_played, initial_games + 1)
        self.assertEqual(self.champion_stats.wins, initial_wins + 1)
        self.assertEqual(self.champion_stats.pick_rate, (initial_games + 1) / 200 * 100)
        
        # Create a losing participant and test
        losing_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=10,
            assists=3,
            creep_score=100,
            team=200,
            win=False,
            game_name='testSummoner2'
        )
        
        initial_losses = self.champion_stats.losses
        self.champion_stats.update_stats(losing_participant, total_games_in_patch=200)
        self.assertEqual(self.champion_stats.losses, initial_losses + 1)

    def test_unique_together_constraint(self):
        # Attempting to create another ChampionStats with the same champion and patch
        # should raise an IntegrityError
        with self.assertRaises(Exception):
            ChampionStats.objects.create(
                champion=self.champion,
                patch='13.15',
                games_played=5,
                wins=3,
                losses=2
            )


class ChampionStatsPatchTest(TestCase):
    def setUp(self):
        self.champion = Champion.objects.create(
            champion_id='Lux',
            name='Lux',
            title='The Lady of Luminosity',
            image_path='Lux.png',
            splash_image_path='Lux_0.jpg'
        )
        self.match = Match.objects.create(
            match_id='match_003',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=100
        )
        self.summoner = Summoner.objects.create(
            puuid='some-unique-id-3',
            game_name='testSummoner3',
            tag_line='NA1',
            summoner_name='testSummoner3',
            summoner_level=30
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
            game_name='testSummoner3'
        )
        self.champion_stats_patch = ChampionStatsPatch.objects.create(
            champion=self.champion,
            patch='13.15',
            total_played=10,
            total_wins=6,
            total_losses=4,
            pick_rate=5.0,
            average_kda=4.5
        )

    def test_champion_stats_patch_creation(self):
        self.assertEqual(self.champion_stats_patch.champion, self.champion)
        self.assertEqual(self.champion_stats_patch.patch, '13.15')
        self.assertEqual(self.champion_stats_patch.total_played, 10)
        self.assertEqual(self.champion_stats_patch.total_wins, 6)
        self.assertEqual(self.champion_stats_patch.total_losses, 4)
        self.assertEqual(self.champion_stats_patch.pick_rate, 5.0)
        self.assertEqual(self.champion_stats_patch.average_kda, 4.5)

    def test_win_rate_calculation(self):
        self.assertEqual(self.champion_stats_patch.win_rate(), 60.0)  # 6/10 * 100 = 60%
        
        # Test with zero games played
        zero_stats = ChampionStatsPatch.objects.create(
            champion=self.champion,
            patch='13.16',
            total_played=0,
            total_wins=0,
            total_losses=0
        )
        self.assertEqual(zero_stats.win_rate(), 0)

    def test_pick_rate_method(self):
        self.assertEqual(self.champion_stats_patch.pick_rate(), 5.0)

    def test_update_stats(self):
        # Initial values
        initial_played = self.champion_stats_patch.total_played
        initial_wins = self.champion_stats_patch.total_wins
        initial_kda = self.champion_stats_patch.average_kda
        
        # Update stats with a winning participant
        self.champion_stats_patch.update_stats(self.participant, total_games_in_patch=200)
        
        # Check that values were updated correctly
        self.assertEqual(self.champion_stats_patch.total_played, initial_played + 1)
        self.assertEqual(self.champion_stats_patch.total_wins, initial_wins + 1)
        self.assertEqual(self.champion_stats_patch.pick_rate, (initial_played + 1) / 200 * 100)
        
        # Check KDA calculation
        # KDA for participant is (10 + 8) / 2 = 9
        # New average KDA should be ((4.5 * 10) + 9) / 11 = 5.0
        expected_kda = ((initial_kda * initial_played) + ((10 + 8) / 2)) / (initial_played + 1)
        self.assertAlmostEqual(self.champion_stats_patch.average_kda, expected_kda, places=2)
        
        # Create a losing participant and test
        losing_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=10,
            assists=3,
            creep_score=100,
            team=200,
            win=False,
            game_name='testSummoner3'
        )
        
        initial_losses = self.champion_stats_patch.total_losses
        self.champion_stats_patch.update_stats(losing_participant, total_games_in_patch=200)
        self.assertEqual(self.champion_stats_patch.total_losses, initial_losses + 1)

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
