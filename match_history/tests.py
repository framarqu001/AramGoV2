from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from .models import *
from .views import analyze_team_composition
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


class TeamCompositionAnalysisTest(TestCase):
    def setUp(self):
        # Create champions
        self.ahri = Champion.objects.create(
            champion_id='Ahri',
            name='Ahri',
            title='The Nine-Tailed Fox',
            image_path='Ahri.png'
        )
        self.yasuo = Champion.objects.create(
            champion_id='Yasuo',
            name='Yasuo',
            title='The Unforgiven',
            image_path='Yasuo.png'
        )
        self.yone = Champion.objects.create(
            champion_id='Yone',
            name='Yone',
            title='The Unforgotten',
            image_path='Yone.png'
        )
        self.darius = Champion.objects.create(
            champion_id='Darius',
            name='Darius',
            title='The Hand of Noxus',
            image_path='Darius.png'
        )
        self.ashe = Champion.objects.create(
            champion_id='Ashe',
            name='Ashe',
            title='The Frost Archer',
            image_path='Ashe.png'
        )
        
        # Create a match
        self.match = Match.objects.create(
            match_id='match_002',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='13.15.1'
        )
        
        # Create summoners
        self.summoners = []
        for i in range(5):
            self.summoners.append(Summoner.objects.create(
                puuid=f'puuid_{i}',
                game_name=f'Player{i}',
                tag_line='NA1',
                summoner_name=f'Player{i}',
                summoner_level=30
            ))
        
        # Create participants with different champions
        self.participants = [
            Participant.objects.create(
                match=self.match,
                summoner=self.summoners[0],
                champion=self.ahri,
                kills=10,
                deaths=2,
                assists=8,
                creep_score=150,
                team=100
            ),
            Participant.objects.create(
                match=self.match,
                summoner=self.summoners[1],
                champion=self.yasuo,
                kills=8,
                deaths=5,
                assists=6,
                creep_score=120,
                team=100
            ),
            Participant.objects.create(
                match=self.match,
                summoner=self.summoners[2],
                champion=self.yone,
                kills=6,
                deaths=4,
                assists=10,
                creep_score=100,
                team=100
            ),
            Participant.objects.create(
                match=self.match,
                summoner=self.summoners[3],
                champion=self.darius,
                kills=12,
                deaths=3,
                assists=4,
                creep_score=180,
                team=100
            ),
            Participant.objects.create(
                match=self.match,
                summoner=self.summoners[4],
                champion=self.ashe,
                kills=5,
                deaths=6,
                assists=15,
                creep_score=90,
                team=100
            )
        ]
    
    def test_analyze_team_composition(self):
        # Test the analyze_team_composition function
        team_comp = analyze_team_composition(self.participants)
        
        # Check that the function returns a dictionary with the expected keys
        self.assertIn('champions', team_comp)
        self.assertIn('damage_distribution', team_comp)
        
        # Check that the damage distribution percentages sum to 100%
        damage_dist = team_comp['damage_distribution']
        self.assertEqual(damage_dist['ap'] + damage_dist['ad'] + damage_dist['true'], 100)
        
        # Check that the champions list has the correct length
        self.assertEqual(len(team_comp['champions']), 5)
        
        # Check that Yasuo and Yone have synergy
        yasuo_yone_synergy = False
        for champion in team_comp['champions']:
            if champion['name'] in ['Yasuo', 'Yone'] and champion['has_synergy']:
                yasuo_yone_synergy = True
                self.assertEqual(champion['synergy_description'], 'Brother synergy')
        
        self.assertTrue(yasuo_yone_synergy, "Yasuo and Yone should have synergy")
        
        # Check damage type distribution
        # In our test data: Ahri (AP), Yasuo (AD), Yone (AD), Darius (True), Ashe (AD)
        # So we expect 1/5 AP, 3/5 AD, 1/5 True
        self.assertEqual(damage_dist['ap'], 20)
        self.assertEqual(damage_dist['ad'], 60)
        self.assertEqual(damage_dist['true'], 20)
