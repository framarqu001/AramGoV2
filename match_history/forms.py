from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Summoner


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with additional fields"""
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=False, help_text="Optional.")
    last_name = forms.CharField(max_length=30, required=False, help_text="Optional.")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            # Create associated UserProfile
            UserProfile.objects.create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with enhanced styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'bio', 'profile_public', 'show_match_history', 
            'show_champion_stats', 'matches_per_page', 'theme_preference'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your display name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell others about yourself...'
            }),
            'matches_per_page': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 50
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class UserForm(forms.ModelForm):
    """Form for editing basic user information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
        }


class SummonerConnectionForm(forms.Form):
    """Form for connecting a Riot Games account"""
    summoner_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Game Name + #Tag (e.g., PlayerName#NA1)',
            'pattern': r'^.+#.+$',
            'title': 'Please enter your summoner name in the format: GameName#Tag'
        }),
        help_text="Enter your Riot Games summoner name in the format: GameName#Tag"
    )
    set_as_primary = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Set this as your primary account for display purposes"
    )

    def clean_summoner_name(self):
        summoner_name = self.cleaned_data['summoner_name']
        if '#' not in summoner_name:
            raise forms.ValidationError("Summoner name must be in the format: GameName#Tag")
        
        try:
            game_name, tag = summoner_name.split('#', 1)
            if not game_name.strip() or not tag.strip():
                raise forms.ValidationError("Both game name and tag are required")
        except ValueError:
            raise forms.ValidationError("Invalid summoner name format")
        
        return summoner_name.strip()


class PrimarySummonerForm(forms.Form):
    """Form for setting primary summoner from connected accounts"""
    primary_summoner = forms.ModelChoiceField(
        queryset=Summoner.objects.none(),
        empty_label="No primary summoner",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, user_profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['primary_summoner'].queryset = user_profile.connected_summoners.all()
        self.fields['primary_summoner'].initial = user_profile.primary_summoner