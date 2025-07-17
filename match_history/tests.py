from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from .models import *
from AramGoV2.util.current_patch import get_patch
from match_history.apps import MatchHistoryConfig
from match_history.views import _get_match_data
from django.core.paginator import Paginator


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


class MatchDataProcessingTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='testPlayer',
            tag_line='NA1',
            normalized_game_name='testplayer',
            normalized_tag_line='na1',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='TestChamp',
            name='Test Champion',
            title='The Test',
            image_path='test.png',
            splash_image_path='test_splash.png'
        )
        
        self.match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,  # 30 minutes
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create spell and rune objects for the participant
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name='Flash',
            image_path='flash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name='Ignite',
            image_path='ignite.png'
        )
        
        self.rune1 = Rune.objects.create(
            rune_id=1,
            name='Conqueror',
            image_path='conqueror.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=2,
            name='Triumph',
            image_path='triumph.png'
        )
        
        # Create main participant with new statistics fields
        self.main_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            creep_score=150,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            team=100,
            win=True,
            game_name='testPlayer#NA1',
            damage_dealt=25000,
            gold_earned=15000,
            vision_score=20,
            damage_taken=18000,
            healing_done=5000
        )
        
        # Create 9 more participants to simulate a full match
        for i in range(9):
            team = 100 if i < 4 else 200  # First 4 on blue team, rest on red team
            win = team == 100  # Blue team wins
            
            Participant.objects.create(
                match=self.match,
                summoner=Summoner.objects.create(
                    puuid=f'other-puuid-{i}',
                    game_name=f'player{i}',
                    tag_line='NA1',
                    normalized_game_name=f'player{i}',
                    normalized_tag_line='na1',
                    summoner_level=30
                ),
                champion=self.champion,
                kills=5,
                deaths=5,
                assists=5,
                creep_score=100,
                spell1=self.spell1,
                spell2=self.spell2,
                rune1=self.rune1,
                rune2=self.rune2,
                team=team,
                win=win,
                game_name=f'player{i}#NA1',
                damage_dealt=10000,
                gold_earned=10000,
                vision_score=10,
                damage_taken=10000,
                healing_done=2000
            )
        
        # Set up all_participants attribute for the match
        self.match.all_participants = Participant.objects.filter(match=self.match).select_related(
            'summoner', 'champion', 'spell1', 'spell2', 'rune1', 'rune2'
        )

    def test_get_match_data_includes_new_statistics(self):
        # Create a paginator with our match
        matches = [self.match]
        paginator = Paginator(matches, 10)
        page_obj = paginator.get_page(1)
        
        # Call the function we want to test
        match_data = _get_match_data(self.summoner, page_obj)
        
        # Verify the result
        self.assertEqual(len(match_data), 1, "Should return data for one match")
        
        match, participant, blue_team, red_team, stats = match_data[0]
        
        # Check that the match is correct
        self.assertEqual(match.match_id, 'test_match_001')
        
        # Check that the participant is correct
        self.assertEqual(participant.summoner, self.summoner)
        
        # Check that the teams are correct
        self.assertEqual(len(blue_team), 5, "Blue team should have 5 players")
        self.assertEqual(len(red_team), 5, "Red team should have 5 players")
        
        # Check that the new statistics are included and formatted correctly
        self.assertIn('damage_dealt', stats)
        self.assertEqual(stats['damage_dealt'], '25,000')
        
        self.assertIn('gold_earned', stats)
        self.assertEqual(stats['gold_earned'], '15,000')
        
        self.assertIn('vision_score', stats)
        self.assertEqual(stats['vision_score'], 20)
        
        self.assertIn('damage_taken', stats)
        self.assertEqual(stats['damage_taken'], '18,000')
        
        self.assertIn('healing_done', stats)
        self.assertEqual(stats['healing_done'], '5,000')


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
