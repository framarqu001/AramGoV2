from django.test import TestCase, Client
from django.urls import reverse
from match_history.models import Match, Summoner, Participant, Champion, SummonerSpell, Rune, Item, ProfileIcon
import json
from datetime import datetime
from django.utils import timezone


class TimelineTests(TestCase):
    def setUp(self):
        # Create test data
        self.profile_icon = ProfileIcon.objects.create(
            profile_id="1",
            image_path="test.png"
        )
        
        self.summoner = Summoner.objects.create(
            puuid="test-puuid",
            game_name="TestPlayer",
            normalized_game_name="testplayer",
            tag_line="NA1",
            normalized_tag_line="na1",
            profile_icon=self.profile_icon
        )
        
        self.champion = Champion.objects.create(
            champion_id="1",
            name="TestChamp",
            title="Test Champion",
            image_path="test.png",
            splash_image_path="test_splash.png"
        )
        
        self.spell1 = SummonerSpell.objects.create(
            spell_id=1,
            name="Flash",
            image_path="flash.png"
        )
        
        self.spell2 = SummonerSpell.objects.create(
            spell_id=2,
            name="Ignite",
            image_path="ignite.png"
        )
        
        self.rune1 = Rune.objects.create(
            rune_id=1,
            name="Conqueror",
            image_path="conqueror.png"
        )
        
        self.rune2 = Rune.objects.create(
            rune_id=2,
            name="Triumph",
            image_path="triumph.png"
        )
        
        self.item = Item.objects.create(
            item_id="1",
            name="Test Item",
            image_path="test_item.png"
        )
        
        # Create a match with timeline data
        self.match = Match.objects.create(
            match_id="TEST123",
            game_start=timezone.now(),
            game_duration=1200,  # 20 minutes
            game_mode="ARAM",
            game_version="14.1.1",
            winner=100,  # Blue team wins
            timeline_data=[
                {
                    "timestamp": 0,
                    "type": "GAME_START",
                    "team": 0,
                    "description": "Game started"
                },
                {
                    "timestamp": 150000,  # 2:30
                    "type": "CHAMPION_KILL",
                    "team": 100,
                    "description": "First Blood!"
                },
                {
                    "timestamp": 600000,  # 10:00
                    "type": "ELITE_MONSTER_KILL",
                    "team": 100,
                    "description": "Blue team secured Rift Herald"
                },
                {
                    "timestamp": 1200000,  # 20:00
                    "type": "GAME_END",
                    "team": 100,
                    "description": "Victory"
                }
            ]
        )
        
        # Create participants
        self.participant = Participant.objects.create(
            match=self.match,
            summoner=self.summoner,
            champion=self.champion,
            kills=10,
            deaths=5,
            assists=15,
            spell1=self.spell1,
            spell2=self.spell2,
            rune1=self.rune1,
            rune2=self.rune2,
            creep_score=100,
            item1=self.item,
            team=100,  # Blue team
            win=True,
            game_name="TestPlayer"
        )
        
        self.client = Client()
        
    def test_timeline_property(self):
        """Test that the timeline_events property correctly formats timeline data"""
        events = self.match.timeline_events
        
        # Check that we have the correct number of events
        self.assertEqual(len(events), 4)
        
        # Check that timestamps are formatted correctly
        self.assertEqual(events[0]['timestamp'], "0:00")
        self.assertEqual(events[1]['timestamp'], "2:30")
        
        # Check that event types are preserved
        self.assertEqual(events[0]['type'], "GAME_START")
        self.assertEqual(events[1]['type'], "CHAMPION_KILL")
        
        # Check that descriptions are preserved
        self.assertEqual(events[0]['description'], "Game started")
        self.assertEqual(events[1]['description'], "First Blood!")
        
    def test_match_detail_view(self):
        """Test that the match detail view includes timeline data"""
        url = reverse('match_history:details', args=[self.summoner.game_name, self.summoner.tag_line])
        response = self.client.get(url)
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the timeline section is in the HTML
        self.assertContains(response, 'match-timeline-section')
        
        # Check that timeline events are in the HTML
        self.assertContains(response, 'First Blood!')
        self.assertContains(response, 'Blue team secured Rift Herald')