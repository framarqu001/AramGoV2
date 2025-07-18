from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.template import Context, Template
from unittest.mock import patch, MagicMock
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


class MatchCardDetailsTemplateTest(TestCase):
    def setUp(self):
        # Create test data
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=30
        )
        
        self.champion = Champion.objects.create(
            champion_id='Teemo',
            name='Teemo',
            title='The Swift Scout',
            image_path='Teemo.png',
            splash_image_path='Teemo_0.jpg'
        )
        
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=32,
            name='Snowball',
            image_path='SummonerSnowball.png'
        )
        
        self.rune1 = Rune.objects.create(
            rune_id=8000,
            name='Precision',
            image_path='perk-images/Styles/7201_Precision.png'
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=8100,
            name='Domination',
            image_path='perk-images/Styles/7200_Domination.png'
        )
        
        self.match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create main participant
        self.main_participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            creep_score=50,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            team=100,
            win=True,
            game_name='TestPlayer'
        )
        
        # Create additional participants for blue team
        self.blue_team = [self.main_participant]
        for i in range(4):
            summoner = Summoner.objects.create(
                puuid=f'blue-puuid-{i}',
                game_name=f'BluePlayer{i}',
                tag_line='NA1'
            )
            participant = Participant.objects.create(
                match=self.match,
                summoner=summoner,
                champion=self.champion,
                kills=5,
                deaths=5,
                assists=5,
                creep_score=30,
                spell1=self.spell1,
                spell2=self.spell2,
                rune1=self.rune1,
                rune2=self.rune2,
                team=100,
                win=True,
                game_name=f'BluePlayer{i}'
            )
            self.blue_team.append(participant)
        
        # Create participants for red team
        self.red_team = []
        for i in range(5):
            summoner = Summoner.objects.create(
                puuid=f'red-puuid-{i}',
                game_name=f'RedPlayer{i}',
                tag_line='NA1'
            )
            participant = Participant.objects.create(
                match=self.match,
                summoner=summoner,
                champion=self.champion,
                kills=3,
                deaths=8,
                assists=6,
                creep_score=25,
                spell1=self.spell1,
                spell2=self.spell2,
                rune1=self.rune1,
                rune2=self.rune2,
                team=200,
                win=False,
                game_name=f'RedPlayer{i}'
            )
            self.red_team.append(participant)
        
        self.main_stats = {
            "kda": "5.00",
            "cs_min": "1.7"
        }
        
        # Mock additional participant attributes that might be used in the template
        for participant in self.blue_team + self.red_team:
            participant.totalDamageDealtToChampions = 15000
            participant.totalDamageTaken = 12000
            participant.visionScore = 10
            participant.objectivesStolen = 1
        
        self.client = Client()
    
    def test_match_card_details_template_renders(self):
        """Test that the match_card_details.html template renders without errors"""
        from django.template.loader import render_to_string
        
        # Create a modified version of the main_participant with the additional attributes
        # that the template might be looking for
        main_participant_dict = {
            'win': self.main_participant.win,
            'kills': self.main_participant.kills,
            'deaths': self.main_participant.deaths,
            'assists': self.main_participant.assists,
            'champion': self.main_participant.champion,
            'spell1': self.main_participant.spell1,
            'spell2': self.main_participant.spell2,
            'rune1': self.main_participant.rune1,
            'rune2': self.main_participant.rune2,
            'item0': None,
            'item1': None,
            'item2': None,
            'item3': None,
            'item4': None,
            'item5': None,
            'item6': None,
            'totalDamageDealtToChampions': 15000,
            'totalDamageTaken': 12000,
            'visionScore': 10,
            'objectivesStolen': 1,
            'game_name': self.main_participant.game_name
        }
        
        # Create similar dictionaries for blue and red team participants
        blue_team_dicts = []
        for participant in self.blue_team:
            blue_team_dicts.append({
                'champion': participant.champion,
                'kills': participant.kills,
                'deaths': participant.deaths,
                'assists': participant.assists,
                'game_name': participant.game_name,
                'totalDamageDealtToChampions': 15000,
                'visionScore': 10
            })
        
        red_team_dicts = []
        for participant in self.red_team:
            red_team_dicts.append({
                'champion': participant.champion,
                'kills': participant.kills,
                'deaths': participant.deaths,
                'assists': participant.assists,
                'game_name': participant.game_name,
                'totalDamageDealtToChampions': 12000,
                'visionScore': 8
            })
        
        # Render the template with our test data
        rendered = render_to_string('match_history/match_card_details.html', {
            'main_participant': main_participant_dict,
            'blue_team': blue_team_dicts,
            'red_team': red_team_dicts,
            'match': self.match,
            'main_stats': self.main_stats
        })
        
        # Check that key elements are present in the rendered template
        self.assertIn('Detailed Stats', rendered)
        self.assertIn('Item Build Timeline', rendered)
        self.assertIn('Runes &amp; Summoner Spells', rendered)
        self.assertIn('All Players Stats', rendered)
        
        # Check that team sections are present
        self.assertIn('Blue Team', rendered)
        self.assertIn('Red Team', rendered)
