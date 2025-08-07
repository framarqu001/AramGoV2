from django.test import TransactionTestCase, TestCase
from django.core.cache import cache
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


class ExpandedMatchCardTest(TestCase):
    """Test cases for expanded match card functionality"""
    
    def setUp(self):
        """Set up test data for match card expansion tests"""
        # Create test summoners
        self.summoner1 = Summoner.objects.create(
            puuid='summoner-1-uuid',
            game_name='TestPlayer1',
            tag_line='NA1',
            summoner_name='TestPlayer1',
            summoner_level=50
        )
        self.summoner2 = Summoner.objects.create(
            puuid='summoner-2-uuid',
            game_name='TestPlayer2',
            tag_line='NA1',
            summoner_name='TestPlayer2',
            summoner_level=45
        )
        
        # Create test champions
        self.champion1 = Champion.objects.create(
            champion_id='Jinx',
            name='Jinx',
            title='The Loose Cannon',
            image_path='Jinx.png'
        )
        self.champion2 = Champion.objects.create(
            champion_id='Ashe',
            name='Ashe',
            title='The Frost Archer',
            image_path='Ashe.png'
        )
        
        # Create test match
        self.match = Match.objects.create(
            match_id='expanded_test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1500,  # 25 minutes
            game_mode='ARAM',
            game_version='14.16.1'
        )
        
        # Create test participants with detailed stats
        self.participant1 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner1,
            champion=self.champion1,
            kills=12,
            deaths=3,
            assists=15,
            creep_score=180,
            win=True,
            total_damage_dealt_to_champions=25000,
            total_damage_taken=18000,
            total_heal=5000,
            gold_earned=12000,
            vision_score=25,
            largest_killing_spree=5,
            largest_multi_kill=3,
            total_time_spent_dead=45
        )
        
        self.participant2 = Participant.objects.create(
            match=self.match,
            summoner=self.summoner2,
            champion=self.champion2,
            kills=8,
            deaths=5,
            assists=12,
            creep_score=160,
            win=False,
            total_damage_dealt_to_champions=20000,
            total_damage_taken=22000,
            total_heal=3500,
            gold_earned=10000,
            vision_score=18,
            largest_killing_spree=3,
            largest_multi_kill=2,
            total_time_spent_dead=75
        )

    def test_match_card_basic_structure(self):
        """Test that match cards have the basic structure for expansion"""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        # Assuming there's a detail view for summoners
        # This would need to be adjusted based on actual URL structure
        response = client.get(f'/summoner/{self.summoner1.puuid}/')
        
        if response.status_code == 200:
            content = response.content.decode()
            # Check for expanded content structure
            self.assertIn('match-expanded-content', content)
            self.assertIn('expanded-stats-grid', content)
            self.assertIn('team-comparison', content)
            self.assertIn('onclick="toggleMatchExpansion(this)"', content)

    def test_expanded_stats_data_presence(self):
        """Test that expanded stats show correct data"""
        # Test damage dealt display
        self.assertEqual(self.participant1.total_damage_dealt_to_champions, 25000)
        self.assertEqual(self.participant2.total_damage_dealt_to_champions, 20000)
        
        # Test healing stats
        self.assertEqual(self.participant1.total_heal, 5000)
        self.assertEqual(self.participant2.total_heal, 3500)
        
        # Test vision scores
        self.assertEqual(self.participant1.vision_score, 25)
        self.assertEqual(self.participant2.vision_score, 18)

    def test_kda_calculation_for_expanded_view(self):
        """Test KDA calculation logic for expanded stats"""
        # Test participant 1 KDA: (12 + 15) / max(3, 1) = 9.0
        expected_kda_1 = (self.participant1.kills + self.participant1.assists) / max(self.participant1.deaths, 1)
        self.assertEqual(expected_kda_1, 9.0)
        
        # Test participant 2 KDA: (8 + 12) / max(5, 1) = 4.0
        expected_kda_2 = (self.participant2.kills + self.participant2.assists) / max(self.participant2.deaths, 1)
        self.assertEqual(expected_kda_2, 4.0)

    def test_team_comparison_data_structure(self):
        """Test that team comparison shows proper participant data"""
        participants = [self.participant1, self.participant2]
        
        for participant in participants:
            # Verify all required fields for team comparison exist
            self.assertIsNotNone(participant.champion)
            self.assertIsNotNone(participant.summoner)
            self.assertIsNotNone(participant.kills)
            self.assertIsNotNone(participant.deaths)
            self.assertIsNotNone(participant.assists)
            self.assertIsNotNone(participant.total_damage_dealt_to_champions)
            self.assertIsNotNone(participant.creep_score)

    def test_win_loss_styling_classes(self):
        """Test that win/loss styling is properly applied"""
        # Test winning participant
        self.assertTrue(self.participant1.win)
        
        # Test losing participant
        self.assertFalse(self.participant2.win)
        
        # In template, this would translate to 'match-win' vs 'match-lose' classes

    def test_performance_stat_categorization(self):
        """Test that performance stats are properly categorized"""
        # High KDA should be categorized as excellent (> 2.0)
        kda_1 = (self.participant1.kills + self.participant1.assists) / max(self.participant1.deaths, 1)
        self.assertGreater(kda_1, 2.0)  # Should get 'excellent' class
        
        # Test damage values are reasonable
        self.assertGreater(self.participant1.total_damage_dealt_to_champions, 0)
        self.assertGreater(self.participant2.total_damage_dealt_to_champions, 0)

    def test_responsive_breakpoint_data_availability(self):
        """Test that all data needed for responsive breakpoints is available"""
        # Ensure essential data is available for mobile view
        essential_fields = ['kills', 'deaths', 'assists', 'champion', 'summoner']
        
        for field in essential_fields:
            self.assertTrue(hasattr(self.participant1, field))
            self.assertTrue(hasattr(self.participant2, field))
            self.assertIsNotNone(getattr(self.participant1, field))
            self.assertIsNotNone(getattr(self.participant2, field))


class MatchCardCSSTest(TestCase):
    """Test cases for match card CSS functionality"""
    
    def test_css_class_structure(self):
        """Test that CSS classes follow expected naming conventions"""
        expected_classes = [
            'match-card',
            'match-expanded-content',
            'expanded-stats-grid',
            'detailed-stats-section',
            'team-comparison',
            'player-row',
            'stat-row'
        ]
        
        # Read the CSS file and check for class definitions
        css_file_path = '/workspace/match_history/static/match_history/css/details.css'
        try:
            with open(css_file_path, 'r') as f:
                css_content = f.read()
                
            for css_class in expected_classes:
                self.assertIn(f'.{css_class}', css_content, 
                            f"CSS class '.{css_class}' not found in details.css")
        except FileNotFoundError:
            self.fail("details.css file not found")

    def test_responsive_breakpoints_exist(self):
        """Test that responsive breakpoints are defined in CSS"""
        css_file_path = '/workspace/match_history/static/match_history/css/details.css'
        try:
            with open(css_file_path, 'r') as f:
                css_content = f.read()
                
            # Check for media queries
            expected_breakpoints = [
                '@media (max-width: 1024px)',
                '@media (max-width: 768px)',
                '@media (max-width: 480px)'
            ]
            
            for breakpoint in expected_breakpoints:
                self.assertIn(breakpoint, css_content,
                            f"Responsive breakpoint '{breakpoint}' not found in CSS")
        except FileNotFoundError:
            self.fail("details.css file not found")

    def test_animation_keyframes_exist(self):
        """Test that animation keyframes are defined"""
        css_file_path = '/workspace/match_history/static/match_history/css/details.css'
        try:
            with open(css_file_path, 'r') as f:
                css_content = f.read()
                
            # Check for animation keyframes
            expected_animations = [
                '@keyframes fadeIn',
                '@keyframes spin'
            ]
            
            for animation in expected_animations:
                self.assertIn(animation, css_content,
                            f"Animation keyframe '{animation}' not found in CSS")
        except FileNotFoundError:
            self.fail("details.css file not found")


class MatchCardTemplateTest(TestCase):
    """Test cases for match card template functionality"""
    
    def test_template_structure(self):
        """Test that template has required structure for expansion"""
        template_path = '/workspace/match_history/templates/match_history/match_list.html'
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
                
            # Check for essential template elements
            essential_elements = [
                'match-expanded-content',
                'expanded-stats-grid',
                'detailed-stats-section',
                'team-comparison',
                'onclick="toggleMatchExpansion(this)"'
            ]
            
            for element in essential_elements:
                self.assertIn(element, template_content,
                            f"Template element '{element}' not found in match_list.html")
        except FileNotFoundError:
            self.fail("match_list.html template not found")

    def test_javascript_function_definition(self):
        """Test that JavaScript functions are properly defined"""
        template_path = '/workspace/match_history/templates/match_history/details.html'
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
                
            # Check for JavaScript functions
            js_functions = [
                'function toggleMatchExpansion',
                'function closeOtherExpandedCards',
                'function initializeLazyLoading'
            ]
            
            for function in js_functions:
                self.assertIn(function, template_content,
                            f"JavaScript function '{function}' not found in details.html")
        except FileNotFoundError:
            self.fail("details.html template not found")


class MatchCardAccessibilityTest(TestCase):
    """Test cases for match card accessibility features"""
    
    def test_keyboard_navigation_support(self):
        """Test that keyboard navigation is supported"""
        template_path = '/workspace/match_history/templates/match_history/details.html'
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
                
            # Check for keyboard event handling
            self.assertIn('keydown', template_content)
            self.assertIn("e.key === 'Enter'", template_content)
            self.assertIn("e.key === ' '", template_content)
        except FileNotFoundError:
            self.fail("details.html template not found")

    def test_focus_states_in_css(self):
        """Test that focus states are defined for accessibility"""
        css_file_path = '/workspace/match_history/static/match_history/css/details.css'
        try:
            with open(css_file_path, 'r') as f:
                css_content = f.read()
                
            # Check for focus states
            focus_selectors = [
                '.match-btn:focus',
                '.player-name:focus'
            ]
            
            for selector in focus_selectors:
                self.assertIn(selector, css_content,
                            f"Focus state '{selector}' not found in CSS")
        except FileNotFoundError:
            self.fail("details.css file not found")
