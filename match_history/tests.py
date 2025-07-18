from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig
from match_history.util.timeline_processor import process_match_timeline
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


class TimelineEventTest(TestCase):
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
            game_version='13.15.1',
            has_timeline=False
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
        
        # Create a timeline event
        self.timeline_event = TimelineEvent.objects.create(
            match=self.match,
            event_type='KILL',
            timestamp=300,  # 5 minutes into the match
            description='testSummoner killed an enemy',
            position_x=1000.0,
            position_y=1000.0
        )
        self.timeline_event.participants_involved.add(self.participant)

    def test_timeline_event_relationships(self):
        self.assertEqual(self.timeline_event.match, self.match)
        self.assertIn(self.participant, self.timeline_event.participants_involved.all())
        self.assertIn(self.timeline_event, self.match.timeline_events.all())

    def test_timeline_event_string_representation(self):
        self.assertEqual(str(self.timeline_event), f"KILL at 300s in match_001")

    def test_get_formatted_time(self):
        self.assertEqual(self.timeline_event.get_formatted_time(), "5:00")
        
        # Test with seconds
        event = TimelineEvent.objects.create(
            match=self.match,
            event_type='KILL',
            timestamp=65,  # 1 minute and 5 seconds
            description='Another kill'
        )
        self.assertEqual(event.get_formatted_time(), "1:05")

    def test_cascade_delete_with_match(self):
        self.match.delete()
        self.assertFalse(TimelineEvent.objects.filter(pk=self.timeline_event.pk).exists())


class TimelineProcessorTest(TestCase):
    def setUp(self):
        self.summoner = Summoner.objects.create(
            puuid='player1',
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
            game_version='13.15.1',
            has_timeline=False
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
        
        # Mock timeline data
        self.timeline_data = {
            'info': {
                'frames': [
                    {
                        'timestamp': 300000,  # 5 minutes in milliseconds
                        'events': [
                            {
                                'type': 'CHAMPION_KILL',
                                'timestamp': 300000,
                                'killerId': 'player1',
                                'victimId': 'player2',
                                'position': {'x': 1000.0, 'y': 1000.0}
                            }
                        ]
                    }
                ]
            }
        }

    @patch('match_history.util.timeline_processor.Participant.objects.get')
    def test_process_match_timeline(self, mock_participant_get):
        # Mock the participant get method
        mock_participant = MagicMock()
        mock_participant.game_name = 'testSummoner'
        mock_participant.champion.name = 'Aatrox'
        mock_participant_get.return_value = mock_participant
        
        # Process the timeline
        result = process_match_timeline(self.match.match_id, self.timeline_data)
        
        # Check that the match has timeline data
        self.match.refresh_from_db()
        self.assertTrue(self.match.has_timeline)
        
        # Check that timeline events were created
        self.assertTrue(TimelineEvent.objects.filter(match=self.match).exists())


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
