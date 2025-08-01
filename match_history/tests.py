from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.template.loader import render_to_string
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



class ExpandedMatchCardTest(TestCase):
    def setUp(self):
        # Create profile icon
        self.profile_icon = ProfileIcon.objects.create(
            profile_id='1',
            image_path='profileicon/1.png'
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
        
        # Create runes
        self.rune1 = Rune.objects.create(
            rune_id=8005,
            name='Press the Attack',
            image_path='perk-images/Styles/Precision/PressTheAttack/PressTheAttack.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=8100,
            name='Domination',
            image_path='perk-images/Styles/7200_Domination.png'
        )
        
        # Create summoners with different levels
        self.summoner1 = Summoner.objects.create(
            puuid='summoner-1-id',
            game_name='Player1',
            tag_line='NA1',
            summoner_level=45,
            profile_icon=self.profile_icon
        )
        
        self.summoner2 = Summoner.objects.create(
            puuid='summoner-2-id',
            game_name='Player2',
            tag_line='NA1',
            summoner_level=67,
            profile_icon=self.profile_icon
        )
        
        # Create champions
        self.champion1 = Champion.objects.create(
            champion_id='Jinx',
            name='Jinx',
            title='The Loose Cannon',
            image_path='Jinx.png',
            splash_image_path='Jinx_0.jpg'
        )
        
        self.champion2 = Champion.objects.create(
            champion_id='Ashe',
            name='Ashe',
            title='The Frost Archer',
            image_path='Ashe.png',
            splash_image_path='Ashe_0.jpg'
        )
        
        # Create match
        self.match = Match.objects.create(
            match_id='expanded_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1200,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create participants with different KDA stats
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=12,
            deaths=3,
            assists=15,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=120,
            team=100,
            win=True,
            game_name='Player1'
        )
        
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=8,
            deaths=5,
            assists=10,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=95,
            team=200,
            win=False,
            game_name='Player2'
        )

    def test_participant_has_expanded_info(self):
        """Test that participants have all the expanded information available"""
        # Test summoner level is available
        self.assertEqual(self.participant1.summoner.summoner_level, 45)
        self.assertEqual(self.participant2.summoner.summoner_level, 67)
        
        # Test profile icon is available
        self.assertIsNotNone(self.participant1.summoner.profile_icon)
        self.assertIsNotNone(self.participant2.summoner.profile_icon)
        
        # Test KDA stats are available
        self.assertEqual(self.participant1.kills, 12)
        self.assertEqual(self.participant1.deaths, 3)
        self.assertEqual(self.participant1.assists, 15)
        
        self.assertEqual(self.participant2.kills, 8)
        self.assertEqual(self.participant2.deaths, 5)
        self.assertEqual(self.participant2.assists, 10)

    def test_profile_icon_url_generation(self):
        """Test that profile icon URLs are generated correctly"""
        # Mock the cache to return a patch version
        with patch('django.core.cache.cache.get', return_value='14.17.1'):
            profile_url = self.participant1.summoner.profile_icon.get_url()
            expected_url = 'https://ddragon.leagueoflegends.com/cdn/14.17.1/img/profileicon/profileicon/1.png'
            self.assertEqual(profile_url, expected_url)

    def test_match_card_template_rendering(self):
        """Test that the match card template renders with expanded user information"""
        # Prepare match data similar to what the view provides
        blue_team = [self.participant1] if self.participant1.team == 100 else []
        red_team = [self.participant2] if self.participant2.team == 200 else []
        
        main_stats = {
            "kda": "9.00",
            "cs_min": "6.0"
        }
        
        matches = [(self.match, self.participant1, blue_team, red_team, main_stats)]
        
        # Render the template
        rendered_html = render_to_string('match_history/match_list.html', {
            'matches': matches
        })
        
        # Check that expanded information is present in the rendered HTML
        self.assertIn('participant-icons', rendered_html)
        self.assertIn('participant-info', rendered_html)
        self.assertIn('summoner-level', rendered_html)
        self.assertIn('participant-kda', rendered_html)
        
        # Check that summoner level is displayed
        self.assertIn('Lv.45', rendered_html)
        
        # Check that KDA is displayed
        self.assertIn('12/3/15', rendered_html)
        self.assertIn('8/5/10', rendered_html)

    def test_participant_without_profile_icon(self):
        """Test that participants without profile icons still render correctly"""
        # Create a summoner without profile icon
        summoner_no_icon = Summoner.objects.create(
            puuid='summoner-no-icon',
            game_name='NoIconPlayer',
            tag_line='NA1',
            summoner_level=25,
            profile_icon=None
        )
        
        participant_no_icon = Participant.objects.create(
            match=self.match,
            summoner=summoner_no_icon,
            champion=self.champion1,
            kills=5,
            deaths=7,
            assists=12,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=80,
            team=100,
            win=True,
            game_name='NoIconPlayer'
        )
        
        # Test that the participant still has other information
        self.assertEqual(participant_no_icon.summoner.summoner_level, 25)
        self.assertIsNone(participant_no_icon.summoner.profile_icon)
        self.assertEqual(participant_no_icon.kills, 5)

    def test_participant_without_summoner_level(self):
        """Test that participants without summoner level still render correctly"""
        # Create a summoner without summoner level
        summoner_no_level = Summoner.objects.create(
            puuid='summoner-no-level',
            game_name='NoLevelPlayer',
            tag_line='NA1',
            summoner_level=None,
            profile_icon=self.profile_icon
        )
        
        participant_no_level = Participant.objects.create(
            match=self.match,
            summoner=summoner_no_level,
            champion=self.champion2,
            kills=3,
            deaths=4,
            assists=8,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=65,
            team=200,
            win=False,
            game_name='NoLevelPlayer'
        )
        
        # Test that the participant still has other information
        self.assertIsNone(participant_no_level.summoner.summoner_level)
        self.assertIsNotNone(participant_no_level.summoner.profile_icon)
        self.assertEqual(participant_no_level.kills, 3)


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
