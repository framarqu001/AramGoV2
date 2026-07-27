from django.test import TestCase
from match_history.models import Participant
from match_history.util.role_classifier import determine_role


class RoleClassifierTests(TestCase):
    def test_determine_role_tank(self):
        """Test that tank champions are correctly classified"""
        self.assertEqual(determine_role('Amumu'), Participant.TANK)
        self.assertEqual(determine_role('Leona'), Participant.TANK)
        self.assertEqual(determine_role('Malphite'), Participant.TANK)
        
    def test_determine_role_bruiser(self):
        """Test that bruiser champions are correctly classified"""
        self.assertEqual(determine_role('Darius'), Participant.BRUISER)
        self.assertEqual(determine_role('Garen'), Participant.BRUISER)
        self.assertEqual(determine_role('Mordekaiser'), Participant.BRUISER)
        
    def test_determine_role_mage(self):
        """Test that mage champions are correctly classified"""
        self.assertEqual(determine_role('Ahri'), Participant.MAGE)
        self.assertEqual(determine_role('Brand'), Participant.MAGE)
        self.assertEqual(determine_role('Lux'), Participant.MAGE)
        
    def test_determine_role_marksman(self):
        """Test that marksman champions are correctly classified"""
        self.assertEqual(determine_role('Ashe'), Participant.MARKSMAN)
        self.assertEqual(determine_role('Caitlyn'), Participant.MARKSMAN)
        self.assertEqual(determine_role('Jinx'), Participant.MARKSMAN)
        
    def test_determine_role_support(self):
        """Test that support champions are correctly classified"""
        self.assertEqual(determine_role('Janna'), Participant.SUPPORT)
        self.assertEqual(determine_role('Lulu'), Participant.SUPPORT)
        self.assertEqual(determine_role('Soraka'), Participant.SUPPORT)
        
    def test_determine_role_assassin(self):
        """Test that assassin champions are correctly classified"""
        self.assertEqual(determine_role('Akali'), Participant.ASSASSIN)
        self.assertEqual(determine_role('Fizz'), Participant.ASSASSIN)
        self.assertEqual(determine_role('Zed'), Participant.ASSASSIN)
        
    def test_determine_role_unknown(self):
        """Test that unknown champions default to MAGE"""
        self.assertEqual(determine_role('NonExistentChampion'), Participant.MAGE)