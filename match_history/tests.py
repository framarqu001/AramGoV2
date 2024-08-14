

from django.test import TransactionTestCase, TestCase
from .models import *


class MatchParticipantDBTest(TransactionTestCase):
    fixtures = ['test_data.json']

    def test_match_has_10_participants(self):
        # Assuming you have a match with a known match_id in your database
        match = Match.objects.get(match_id="NA1_5010881966")
        participants_count = match.participants.count()
        self.assertEqual(participants_count, 10, f"Match has {participants_count} participants, expected 10")


class MatchParticipantTest(TestCase):
    def test_participant_relationships(self):
        summoner = Summoner.objects.create(
            puuid='some-unique-id',
            game_name='TestGame',
            summoner_name='TestSummoner',
            summoner_level=30
        )
        champion = Champion.objects.create(
            champion_id='1',
            name='Aatrox',
            title='The Darkin Blade',
            image_path='Aatrox.png'
        )
        match = Match.objects.create(
            match_id='match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='Classic',
            game_version='13.15.1'
        )
        participant = Participant.objects.create(
            match=match,
            summoner=summoner,
            champion=champion,
            kills=10,
            deaths=2,
            assists=8,
            creep_score=150
        )

        self.assertEqual(participant.match, match)
        self.assertEqual(participant.summoner, summoner)
        self.assertEqual(participant.champion, champion)
        self.assertIn(participant, match.participants.all())
