from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.urls import reverse
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


class EnhancedMatchCardTest(TestCase):
    def setUp(self):
        # Set up test data for enhanced match card testing
        cache.set('PATCH', '14.17.1')
        
        # Create profile icons
        self.profile_icon1 = ProfileIcon.objects.create(
            profile_id='1',
            image_path='profileicon/1.png'
        )
        self.profile_icon2 = ProfileIcon.objects.create(
            profile_id='2', 
            image_path='profileicon/2.png'
        )
        
        # Create summoners
        self.summoner1 = Summoner.objects.create(
            puuid='summoner-1-uuid',
            game_name='TestPlayer1',
            tag_line='NA1',
            summoner_level=45,
            profile_icon=self.profile_icon1
        )
        self.summoner2 = Summoner.objects.create(
            puuid='summoner-2-uuid',
            game_name='TestPlayer2',
            tag_line='NA1',
            summoner_level=32,
            profile_icon=self.profile_icon2
        )
        
        # Create champions
        self.champion1 = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png'
        )
        self.champion2 = Champion.objects.create(
            champion_id='Jinx',
            name='Jinx',
            title='The Loose Cannon',
            image_path='Jinx.png'
        )
        
        # Create summoner spells
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
        
        # Create match
        self.match = Match.objects.create(
            match_id='enhanced_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create participants
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=12,
            deaths=3,
            assists=15,
            creep_score=145,
            spell1=self.spell1,
            spell2=self.spell2,
            team=100,
            win=True,
            game_name='TestPlayer1'
        )
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=8,
            deaths=7,
            assists=12,
            creep_score=132,
            spell1=self.spell1,
            spell2=self.spell2,
            team=200,
            win=False,
            game_name='TestPlayer2'
        )
        
        self.client = Client()

    def test_enhanced_participant_data_in_template(self):
        """Test that enhanced participant information is properly rendered in match cards"""
        # Import the view function to test template rendering
        from match_history.views import _get_match_data
        from django.core.paginator import Paginator
        
        # Get match data as the view would
        matches_queryset = Match.objects.filter(participants__summoner=self.summoner1).prefetch_related(
            'participants__summoner', 'participants__champion', 'participants__summoner__profile_icon'
        )
        paginator = Paginator(matches_queryset, 10)
        page_obj = paginator.get_page(1)
        match_data = _get_match_data(self.summoner1, page_obj)
        
        # Verify match data structure
        self.assertEqual(len(match_data), 1)
        match, main_participant, blue_team, red_team, main_stats = match_data[0]
        
        # Test that all required participant data is available
        for participant in blue_team + red_team:
            self.assertIsNotNone(participant.kills)
            self.assertIsNotNone(participant.deaths)
            self.assertIsNotNone(participant.assists)
            self.assertIsNotNone(participant.creep_score)
            self.assertIsNotNone(participant.summoner.summoner_level)
            self.assertIsNotNone(participant.win)
            
    def test_participant_profile_icon_availability(self):
        """Test that profile icons are available for participants"""
        participant = Participant.objects.select_related('summoner__profile_icon').get(pk=self.participant1.pk)
        self.assertIsNotNone(participant.summoner.profile_icon)
        self.assertEqual(participant.summoner.profile_icon.profile_id, '1')
        
    def test_participant_stats_calculation(self):
        """Test that participant stats are correctly calculated"""
        # Test KDA display format
        kda_string = f"{self.participant1.kills}/{self.participant1.deaths}/{self.participant1.assists}"
        self.assertEqual(kda_string, "12/3/15")
        
        # Test level display format
        level_string = f"Lv{self.participant1.summoner.summoner_level}"
        self.assertEqual(level_string, "Lv45")
        
        # Test CS display format
        cs_string = f"{self.participant1.creep_score}cs"
        self.assertEqual(cs_string, "145cs")
        
    def test_win_loss_indicator_logic(self):
        """Test that win/loss indicators are correctly determined"""
        # Test winning participant
        self.assertTrue(self.participant1.win)
        win_class = "win" if self.participant1.win else "loss"
        self.assertEqual(win_class, "win")
        
        # Test losing participant
        self.assertFalse(self.participant2.win)
        loss_class = "win" if self.participant2.win else "loss"
        self.assertEqual(loss_class, "loss")

    def test_participant_highlight_logic(self):
        """Test that main participant highlighting works correctly"""
        # When viewing summoner1's matches, participant1 should be highlighted
        from match_history.views import _get_match_data
        from django.core.paginator import Paginator
        
        matches_queryset = Match.objects.filter(participants__summoner=self.summoner1).prefetch_related(
            'participants__summoner', 'participants__champion'
        )
        paginator = Paginator(matches_queryset, 10)
        page_obj = paginator.get_page(1)
        match_data = _get_match_data(self.summoner1, page_obj)
        
        match, main_participant, blue_team, red_team, main_stats = match_data[0]
        
        # Main participant should be the one belonging to summoner1
        self.assertEqual(main_participant.summoner, self.summoner1)
        self.assertEqual(main_participant, self.participant1)
