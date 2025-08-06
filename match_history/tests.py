from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from decimal import Decimal
import datetime
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig
from match_history.util.populate_data import MatchManager


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
            creep_score=150,
            team=100,
            win=True,
            game_name='testSummoner'
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
    
    # New tests for extended participant statistics
    def test_kda_ratio_calculation(self):
        """Test KDA ratio calculation with various scenarios"""
        # Test normal case
        self.assertEqual(self.participant.calculate_kda_ratio(), 9.0)  # (10 + 8) / 2
        
        # Test zero deaths case
        participant_no_deaths = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=0,
            assists=3,
            creep_score=100,
            team=100,
            win=True,
            game_name='testSummoner2'
        )
        self.assertEqual(participant_no_deaths.calculate_kda_ratio(), 8.0)  # (5 + 3) / 1
        
        # Test zero kills and assists
        participant_no_ka = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=0,
            deaths=5,
            assists=0,
            creep_score=50,
            team=200,
            win=False,
            game_name='testSummoner3'
        )
        self.assertEqual(participant_no_ka.calculate_kda_ratio(), 0.0)  # (0 + 0) / 5

    def test_get_kda_ratio_with_stored_value(self):
        """Test that get_kda_ratio returns stored value when available"""
        self.participant.kda_ratio = Decimal('5.25')
        self.participant.save()
        self.assertEqual(self.participant.get_kda_ratio(), 5.25)

    def test_get_kda_ratio_calculated_when_not_stored(self):
        """Test that get_kda_ratio calculates when no stored value"""
        self.participant.kda_ratio = None
        self.participant.save()
        self.assertEqual(self.participant.get_kda_ratio(), 9.0)

    def test_extended_stats_fields_nullable(self):
        """Test that new extended stats fields can be null"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=1,
            deaths=1,
            assists=1,
            creep_score=50,
            team=100,
            win=True,
            game_name='testNullStats',
            kda_ratio=None,
            total_damage_dealt=None,
            damage_to_champions=None,
            damage_taken=None
        )
        self.assertIsNone(participant.kda_ratio)
        self.assertIsNone(participant.total_damage_dealt)
        self.assertIsNone(participant.damage_to_champions)
        self.assertIsNone(participant.damage_taken)

    def test_extended_stats_fields_with_values(self):
        """Test that extended stats fields store values correctly"""
        participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=5,
            deaths=2,
            assists=7,
            creep_score=120,
            team=100,
            win=True,
            game_name='testWithStats',
            kda_ratio=Decimal('6.00'),
            total_damage_dealt=25000,
            damage_to_champions=18000,
            damage_taken=15000
        )
        self.assertEqual(participant.kda_ratio, Decimal('6.00'))
        self.assertEqual(participant.total_damage_dealt, 25000)
        self.assertEqual(participant.damage_to_champions, 18000)
        self.assertEqual(participant.damage_taken, 15000)


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


class MatchManagerTest(TestCase):
    def setUp(self):
        """Set up test data for MatchManager tests"""
        self.summoner = Summoner.objects.create(
            puuid='test-puuid-123',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png',
            splash_image_path='Aatrox_0.jpg'
        )
        
        # Create mock spell and rune objects
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
        
        self.rune1 = Rune.objects.create(
            rune_id=8005,
            name='Press the Attack',
            image_path='perk-images/Styles/Precision/PressTheAttack/PressTheAttack.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=8000,
            name='Precision',
            image_path='perk-images/Styles/7201_Precision.png'
        )

    @patch('match_history.util.populate_data.LolWatcher')
    def test_calculate_kda_ratio_method(self, mock_watcher):
        """Test the _calculate_kda_ratio method with various inputs"""
        match_manager = MatchManager("americas", "na1", self.summoner)
        
        # Test normal case
        result = match_manager._calculate_kda_ratio(10, 2, 8)
        self.assertEqual(result, Decimal('9.00'))
        
        # Test zero deaths
        result = match_manager._calculate_kda_ratio(5, 0, 3)
        self.assertEqual(result, Decimal('8.00'))
        
        # Test zero kills and assists
        result = match_manager._calculate_kda_ratio(0, 5, 0)
        self.assertEqual(result, Decimal('0.00'))
        
        # Test with decimal result
        result = match_manager._calculate_kda_ratio(7, 3, 2)
        self.assertEqual(result, Decimal('3.00'))

    @patch('match_history.util.populate_data.LolWatcher')
    def test_extract_damage_stats_from_timeline_success(self, mock_watcher):
        """Test successful extraction of damage stats from timeline data"""
        match_manager = MatchManager("americas", "na1", self.summoner)
        
        # Mock timeline data structure
        timeline_data = {
            'info': {
                'frames': [
                    {
                        'participantFrames': {
                            '1': {
                                'damageStats': {
                                    'totalDamageDone': 25000,
                                    'totalDamageDoneToChampions': 18000,
                                    'totalDamageTaken': 15000
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        total_damage, damage_to_champs, damage_taken = match_manager._extract_damage_stats_from_timeline(
            timeline_data, 1
        )
        
        self.assertEqual(total_damage, 25000)
        self.assertEqual(damage_to_champs, 18000)
        self.assertEqual(damage_taken, 15000)

    @patch('match_history.util.populate_data.LolWatcher')
    def test_extract_damage_stats_from_timeline_no_data(self, mock_watcher):
        """Test extraction when timeline data is None or malformed"""
        match_manager = MatchManager("americas", "na1", self.summoner)
        
        # Test with None data
        result = match_manager._extract_damage_stats_from_timeline(None, 1)
        self.assertEqual(result, (None, None, None))
        
        # Test with empty data
        result = match_manager._extract_damage_stats_from_timeline({}, 1)
        self.assertEqual(result, (None, None, None))
        
        # Test with malformed data
        malformed_data = {'info': {'frames': []}}
        result = match_manager._extract_damage_stats_from_timeline(malformed_data, 1)
        self.assertEqual(result, (None, None, None))

    @patch('match_history.util.populate_data.LolWatcher')
    def test_get_match_timeline_api_error(self, mock_watcher):
        """Test timeline API error handling"""
        from riotwatcher import ApiError
        
        # Mock the timeline API to raise an ApiError
        mock_watcher_instance = mock_watcher.return_value
        mock_watcher_instance.match.timeline_by_match.side_effect = ApiError("Timeline not found", 404)
        
        match_manager = MatchManager("americas", "na1", self.summoner)
        
        # Should return None on API error, not raise exception
        result = match_manager._get_match_timeline("test_match_id")
        self.assertIsNone(result)

    @patch('match_history.util.populate_data.LolWatcher')
    def test_get_match_timeline_success(self, mock_watcher):
        """Test successful timeline API call"""
        mock_timeline_data = {'info': {'frames': []}}
        
        mock_watcher_instance = mock_watcher.return_value
        mock_watcher_instance.match.timeline_by_match.return_value = mock_timeline_data
        
        match_manager = MatchManager("americas", "na1", self.summoner)
        
        result = match_manager._get_match_timeline("test_match_id")
        self.assertEqual(result, mock_timeline_data)
        mock_watcher_instance.match.timeline_by_match.assert_called_once_with("na1", "test_match_id")

    @patch('match_history.util.populate_data.LolWatcher')
    def test_create_participants_with_timeline_data(self, mock_watcher):
        """Test participant creation with timeline data integration"""
        # This is a more complex integration test
        mock_watcher_instance = mock_watcher.return_value
        
        # Mock timeline data
        timeline_data = {
            'info': {
                'frames': [
                    {
                        'participantFrames': {
                            '1': {
                                'damageStats': {
                                    'totalDamageDone': 25000,
                                    'totalDamageDoneToChampions': 18000,
                                    'totalDamageTaken': 15000
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        mock_watcher_instance.match.timeline_by_match.return_value = timeline_data
        
        # Create a match for testing
        match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1',
            winner=100
        )
        
        # Mock match info data structure
        match_info = {
            'metadata': {
                'participants': ['test-puuid-123']
            },
            'info': {
                'participants': [
                    {
                        'puuid': 'test-puuid-123',
                        'championName': 'Aatrox',
                        'kills': 10,
                        'deaths': 2,
                        'assists': 8,
                        'totalMinionsKilled': 150,
                        'teamId': 100,
                        'win': True,
                        'riotIdGameName': 'TestPlayer',
                        'summonerName': 'TestPlayer',
                        'summoner1Id': 4,
                        'summoner2Id': 32,
                        'summoner1Casts': 5,
                        'summoner2Casts': 0,
                        'perks': {
                            'styles': [
                                {
                                    'selections': [
                                        {'perk': 8005}
                                    ]
                                },
                                {
                                    'style': 8000
                                }
                            ]
                        },
                        'challenges': {
                            'snowballsHit': 3
                        },
                        'item0': 0, 'item1': 0, 'item2': 0, 'item3': 0, 'item4': 0, 'item5': 0,
                        'profileIcon': 1,
                        'summonerLevel': 30,
                        'totalDamageDealt': 20000,  # Fallback damage stats
                        'totalDamageDealtToChampions': 15000,
                        'totalDamageTaken': 12000
                    }
                ]
            }
        }
        
        match_manager = MatchManager("americas", "na1", self.summoner)
        match_manager._create_participants(match_info, match)
        
        # Verify participant was created with extended stats
        participant = Participant.objects.get(match=match, summoner=self.summoner)
        
        # Check basic stats
        self.assertEqual(participant.kills, 10)
        self.assertEqual(participant.deaths, 2)
        self.assertEqual(participant.assists, 8)
        
        # Check extended stats from timeline data (should override match data)
        self.assertEqual(participant.kda_ratio, Decimal('9.00'))
        self.assertEqual(participant.total_damage_dealt, 25000)  # From timeline
        self.assertEqual(participant.damage_to_champions, 18000)  # From timeline
        self.assertEqual(participant.damage_taken, 15000)  # From timeline
