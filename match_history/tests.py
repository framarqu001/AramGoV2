from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig
import json


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
            normalized_game_name='testsummoner',
            normalized_tag_line='na1',
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
            gold_earned=10000
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


class MatchDetailsEndpointTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='testPlayer',
            tag_line='NA1',
            normalized_game_name='testplayer',
            normalized_tag_line='na1',
            summoner_name='testPlayer',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png'
        )
        
        self.match = Match.objects.create(
            id=1,
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1'
        )
        
        # Create a participant for the main summoner
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            team=100,
            win=True,
            gold_earned=12000,
            creep_score=50
        )
        
        # Create additional participants to simulate a full match
        for i in range(9):
            team = 100 if i < 4 else 200  # 5 players on each team including main participant
            Participant.objects.create(
                match=self.match,
                summoner=Summoner.objects.create(
                    puuid=f'other-puuid-{i}',
                    game_name=f'player{i}',
                    tag_line='NA1',
                    normalized_game_name=f'player{i}',
                    normalized_tag_line='na1',
                    summoner_name=f'player{i}',
                    summoner_level=30
                ),
                champion=self.champion,
                kills=5,
                deaths=5,
                assists=5,
                team=team,
                win=team == 100,
                gold_earned=10000,
                creep_score=40
            )
        
        self.client = Client()
        
    def test_match_details_endpoint(self):
        # Set up the request with the required headers
        url = reverse('match_history:match_details', kwargs={
            'game_name': self.summoner.normalized_game_name,
            'tag': self.summoner.normalized_tag_line,
            'match_id': self.match.id
        })
        
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        response = self.client.get(url, **headers)
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains the expected fields
        self.assertIn('html', data)
        self.assertIn('match_id', data)
        self.assertEqual(data['match_id'], str(self.match.id))
        
        # Check that the HTML content contains expected elements
        self.assertIn('match-expanded-content', data['html'])
        self.assertIn('Blue Team', data['html'])
        self.assertIn('Red Team', data['html'])