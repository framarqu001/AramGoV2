#!/usr/bin/env python
"""
Simple test script to verify the expanded match cards functionality
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

from django.template.loader import render_to_string
from match_history.models import *
import datetime

def test_expanded_match_cards():
    print("Testing expanded match cards functionality...")
    
    try:
        # Create test data
        profile_icon = ProfileIcon.objects.create(
            profile_id='test_icon',
            image_path='profileicon/1.png'
        )
        
        summoner = Summoner.objects.create(
            puuid='test-summoner-id',
            game_name='TestPlayer',
            tag_line='NA1',
            summoner_level=50,
            profile_icon=profile_icon
        )
        
        champion = Champion.objects.create(
            champion_id='TestChamp',
            name='Test Champion',
            title='The Test',
            image_path='TestChamp.png',
            splash_image_path='TestChamp_0.jpg'
        )
        
        spell1 = SummonerSpell.objects.create(
            spell_id=4,
            name='Flash',
            image_path='SummonerFlash.png'
        )
        
        spell2 = SummonerSpell.objects.create(
            spell_id=32,
            name='Mark',
            image_path='SummonerSnowball.png'
        )
        
        rune1 = Rune.objects.create(
            rune_id=8005,
            name='Press the Attack',
            image_path='perk-images/Styles/Precision/PressTheAttack/PressTheAttack.png'
        )
        
        rune2 = Rune.objects.create(
            rune_id=8100,
            name='Domination',
            image_path='perk-images/Styles/7200_Domination.png'
        )
        
        match = Match.objects.create(
            match_id='test_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1200,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        participant = Participant.objects.create(
            match=match,
            summoner=summoner,
            champion=champion,
            kills=10,
            deaths=2,
            assists=8,
            spell1=spell1,
            spell2=spell2,
            rune1=rune1,
            rune2=rune2,
            creep_score=150,
            team=100,
            win=True,
            game_name='TestPlayer'
        )
        
        # Test data structure
        blue_team = [participant]
        red_team = []
        main_stats = {"kda": "9.00", "cs_min": "7.5"}
        matches = [(match, participant, blue_team, red_team, main_stats)]
        
        # Render template
        rendered_html = render_to_string('match_history/match_list.html', {
            'matches': matches
        })
        
        # Check for expanded information
        checks = [
            ('participant-icons', 'Participant icons container'),
            ('participant-info', 'Participant info container'),
            ('summoner-level', 'Summoner level class'),
            ('participant-kda', 'Participant KDA class'),
            ('Lv.50', 'Summoner level display'),
            ('10/2/8', 'KDA display'),
            ('TestPlayer', 'Player name')
        ]
        
        all_passed = True
        for check, description in checks:
            if check in rendered_html:
                print(f"✓ {description} found in rendered HTML")
            else:
                print(f"✗ {description} NOT found in rendered HTML")
                all_passed = False
        
        if all_passed:
            print("\n🎉 All tests passed! Expanded match cards are working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            
        # Clean up test data
        match.delete()
        summoner.delete()
        champion.delete()
        profile_icon.delete()
        spell1.delete()
        spell2.delete()
        rune1.delete()
        rune2.delete()
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_expanded_match_cards()