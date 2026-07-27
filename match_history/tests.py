from django.test import TransactionTestCase, TestCase, Client
from django.core.cache import cache
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
import datetime
from .models import *
from .forms import CustomUserCreationForm, UserProfileForm, SummonerConnectionForm
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


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.summoner = Summoner.objects.create(
            puuid='test-puuid-123',
            game_name='TestPlayer',
            normalized_game_name='testplayer',
            tag_line='NA1',
            normalized_tag_line='na1',
            summoner_level=50
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            display_name='Test Display Name',
            bio='Test bio',
            primary_summoner=self.summoner
        )
        self.profile.connected_summoners.add(self.summoner)

    def test_user_profile_creation(self):
        """Test that UserProfile is created correctly"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.display_name, 'Test Display Name')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.primary_summoner, self.summoner)
        self.assertTrue(self.profile.profile_public)
        self.assertTrue(self.profile.show_match_history)
        self.assertTrue(self.profile.show_champion_stats)
        self.assertEqual(self.profile.matches_per_page, 10)
        self.assertEqual(self.profile.theme_preference, 'dark')

    def test_get_display_name(self):
        """Test get_display_name method"""
        self.assertEqual(self.profile.get_display_name(), 'Test Display Name')
        
        # Test fallback to username when display_name is empty
        self.profile.display_name = ''
        self.profile.save()
        self.assertEqual(self.profile.get_display_name(), 'testuser')

    def test_get_primary_summoner_name(self):
        """Test get_primary_summoner_name method"""
        self.assertEqual(self.profile.get_primary_summoner_name(), 'TestPlayer#NA1')
        
        # Test when no primary summoner is set
        self.profile.primary_summoner = None
        self.profile.save()
        self.assertIsNone(self.profile.get_primary_summoner_name())

    def test_has_connected_summoners(self):
        """Test has_connected_summoners method"""
        self.assertTrue(self.profile.has_connected_summoners())
        
        # Test when no summoners are connected
        self.profile.connected_summoners.clear()
        self.assertFalse(self.profile.has_connected_summoners())

    def test_can_view_profile(self):
        """Test can_view_profile method"""
        other_user = User.objects.create_user(username='otheruser', password='pass123')
        
        # Public profile should be viewable by anyone
        self.assertTrue(self.profile.can_view_profile())
        self.assertTrue(self.profile.can_view_profile(other_user))
        self.assertTrue(self.profile.can_view_profile(self.user))
        
        # Private profile should only be viewable by owner
        self.profile.profile_public = False
        self.profile.save()
        self.assertFalse(self.profile.can_view_profile(other_user))
        self.assertTrue(self.profile.can_view_profile(self.user))

    def test_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.profile), 'Profile for testuser')


class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration_view(self):
        """Test user registration view"""
        response = self.client.get(reverse('match_history:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join AramGo')

    def test_user_registration_post(self):
        """Test user registration with POST data"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(reverse('match_history:register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check that UserProfile was created
        user = User.objects.get(username='newuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_login_view(self):
        """Test user login view"""
        response = self.client.get(reverse('match_history:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login to AramGo')

    def test_user_login_post(self):
        """Test user login with POST data"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('match_history:login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_user_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('match_history:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('match_history:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('match_history:profile'))
        self.assertEqual(response.status_code, 200)


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.summoner = Summoner.objects.create(
            puuid='test-puuid-123',
            game_name='TestPlayer',
            normalized_game_name='testplayer',
            tag_line='NA1',
            normalized_tag_line='na1',
            summoner_level=50
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_profile_settings_view(self):
        """Test profile settings view"""
        response = self.client.get(reverse('match_history:profile_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile Settings')

    def test_profile_settings_post(self):
        """Test updating profile settings"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'display_name': 'Updated Display Name',
            'bio': 'Updated bio',
            'profile_public': True,
            'show_match_history': True,
            'show_champion_stats': True,
            'matches_per_page': 15,
            'theme_preference': 'light'
        }
        response = self.client.post(reverse('match_history:profile_settings'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check that profile was updated
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Updated Display Name')
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.matches_per_page, 15)
        self.assertEqual(self.profile.theme_preference, 'light')
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_connect_summoner_view(self):
        """Test connect summoner view"""
        response = self.client.get(reverse('match_history:connect_summoner'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connect Riot Games Account')

    @patch('match_history.views.SummonerManager')
    def test_connect_existing_summoner(self, mock_summoner_manager):
        """Test connecting an existing summoner"""
        data = {
            'summoner_name': 'TestPlayer#NA1',
            'set_as_primary': True
        }
        response = self.client.post(reverse('match_history:connect_summoner'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful connection
        
        # Check that summoner was connected
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.connected_summoners.filter(puuid=self.summoner.puuid).exists())
        self.assertEqual(self.profile.primary_summoner, self.summoner)

    def test_disconnect_summoner(self):
        """Test disconnecting a summoner"""
        self.profile.connected_summoners.add(self.summoner)
        self.profile.primary_summoner = self.summoner
        self.profile.save()
        
        response = self.client.get(
            reverse('match_history:disconnect_summoner', args=[self.summoner.puuid])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after disconnection
        
        # Check that summoner was disconnected
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.connected_summoners.filter(puuid=self.summoner.puuid).exists())
        self.assertIsNone(self.profile.primary_summoner)

    def test_set_primary_summoner_view(self):
        """Test set primary summoner view"""
        self.profile.connected_summoners.add(self.summoner)
        response = self.client.get(reverse('match_history:set_primary_summoner'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set Primary Summoner')


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)

    def test_custom_user_creation_form_valid(self):
        """Test CustomUserCreationForm with valid data"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_creates_profile(self):
        """Test that CustomUserCreationForm creates UserProfile"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_profile_form_valid(self):
        """Test UserProfileForm with valid data"""
        form_data = {
            'display_name': 'Test Display',
            'bio': 'Test bio',
            'profile_public': True,
            'show_match_history': True,
            'show_champion_stats': True,
            'matches_per_page': 15,
            'theme_preference': 'light'
        }
        form = UserProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_summoner_connection_form_valid(self):
        """Test SummonerConnectionForm with valid data"""
        form_data = {
            'summoner_name': 'TestPlayer#NA1',
            'set_as_primary': True
        }
        form = SummonerConnectionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_summoner_connection_form_invalid_format(self):
        """Test SummonerConnectionForm with invalid summoner name format"""
        form_data = {
            'summoner_name': 'TestPlayerWithoutTag',
            'set_as_primary': True
        }
        form = SummonerConnectionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('summoner_name', form.errors)


class NavigationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_navigation_anonymous_user(self):
        """Test navigation links for anonymous users"""
        response = self.client.get(reverse('match_history:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertNotContains(response, 'Profile')
        self.assertNotContains(response, 'Logout')

    def test_navigation_authenticated_user(self):
        """Test navigation links for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('match_history:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, 'Login')
        self.assertNotContains(response, 'Register')
