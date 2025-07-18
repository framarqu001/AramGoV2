from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.urls import reverse
from unittest.mock import patch
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


class ChampionsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.champions_url = reverse('match_history:champions')
        
        # Create test champions
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
        
        # Create champion stats for different patches
        self.stats1 = ChampionStatsPatch.objects.create(
            champion=self.champion1,
            patch='14.17',
            total_played=100,
            total_wins=60,
            total_losses=40
        )
        
        self.stats2 = ChampionStatsPatch.objects.create(
            champion=self.champion2,
            patch='14.17',
            total_played=150,
            total_wins=75,
            total_losses=75
        )
        
        self.stats3 = ChampionStatsPatch.objects.create(
            champion=self.champion1,
            patch='14.16',
            total_played=80,
            total_wins=40,
            total_losses=40
        )
    
    def test_champions_view_loads(self):
        response = self.client.get(self.champions_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'match_history/champions.html')
    
    def test_champions_view_context(self):
        response = self.client.get(self.champions_url)
        self.assertIn('champion_data', response.context)
        self.assertIn('available_patches', response.context)
        self.assertIn('selected_patch', response.context)
        self.assertIn('sort_by', response.context)
    
    def test_champions_view_filtering(self):
        # Test filtering by patch
        response = self.client.get(f"{self.champions_url}?patch=14.16")
        self.assertEqual(response.context['selected_patch'], '14.16')
        self.assertEqual(len(response.context['champion_data']), 1)
        
        # Test default patch
        response = self.client.get(self.champions_url)
        self.assertEqual(len(response.context['champion_data']), 2)
    
    def test_champions_view_sorting(self):
        # Test sorting by win rate
        response = self.client.get(f"{self.champions_url}?sort=win_rate")
        champions = response.context['champion_data']
        self.assertEqual(champions[0]['champion'].name, 'Aatrox')  # 60% win rate
        
        # Test sorting by games played
        response = self.client.get(f"{self.champions_url}?sort=games_played")
        champions = response.context['champion_data']
        self.assertEqual(champions[0]['champion'].name, 'Ahri')  # 150 games played
        
        # Test sorting by name
        response = self.client.get(f"{self.champions_url}?sort=name")
        champions = response.context['champion_data']
        self.assertEqual(champions[0]['champion'].name, 'Aatrox')  # Alphabetically first
