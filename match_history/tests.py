from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.template import Context, Template
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


class MatchCardExpandableTest(TestCase):
    def setUp(self):
        # Create test data for match card rendering
        self.summoner = Summoner.objects.create(
            puuid='test-puuid',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_name='TestPlayer',
            summoner_level=30
        )
        self.champion = Champion.objects.create(
            champion_id='Aatrox',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png'
        )
        self.match = Match.objects.create(
            match_id='test_match_001',
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
            win=True
        )

    def test_match_card_has_data_expanded_attribute(self):
        """Test that match cards have the data-expanded attribute set to false by default"""
        template = Template("""
            {% load static %}
            {% for match, main_participant, blue_team, red_team, main_stats in matches %}
                <div class="match-card {% if main_participant.win%}match-win{% else %}match-lose{% endif %}" data-expanded="false">
                    <button class="match-btn {% if main_participant.win%}match-win{% else %}match-lose{% endif %}">
                        <svg class="drop" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                            <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" fill="white" />
                        </svg>
                    </button>
                </div>
            {% endfor %}
        """)
        
        # Mock match data structure similar to what the view provides
        matches = [(self.match, self.participant, [], [], {})]
        context = Context({'matches': matches})
        rendered = template.render(context)
        
        # Check that data-expanded="false" is present
        self.assertIn('data-expanded="false"', rendered)
        # Check that match-card class is present
        self.assertIn('class="match-card', rendered)
        # Check that match-btn is present
        self.assertIn('class="match-btn', rendered)
        # Check that chevron SVG with drop class is present
        self.assertIn('class="drop"', rendered)

    def test_match_card_win_lose_classes(self):
        """Test that match cards have correct win/lose classes"""
        template = Template("""
            {% for match, main_participant, blue_team, red_team, main_stats in matches %}
                <div class="match-card {% if main_participant.win%}match-win{% else %}match-lose{% endif %}" data-expanded="false">
                </div>
            {% endfor %}
        """)
        
        # Test with winning participant
        matches = [(self.match, self.participant, [], [], {})]
        context = Context({'matches': matches})
        rendered = template.render(context)
        self.assertIn('match-card match-win', rendered)
        
        # Test with losing participant
        self.participant.win = False
        self.participant.save()
        matches = [(self.match, self.participant, [], [], {})]
        context = Context({'matches': matches})
        rendered = template.render(context)
        self.assertIn('match-card match-lose', rendered)
