#!/usr/bin/env python
"""
Simple test script to verify enhanced match card functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

from match_history.models import *
from django.template import Template, Context
from django.core.cache import cache
import datetime

def test_enhanced_match_cards():
    """Test the enhanced match card template rendering"""
    print("Testing enhanced match card functionality...")
    
    # Set cache for patch version
    cache.set('PATCH', '14.17.1')
    
    # Create test data
    try:
        # Clean up any existing test data
        Match.objects.filter(match_id__startswith='test_').delete()
        Summoner.objects.filter(puuid__startswith='test_').delete()
        
        # Create profile icons
        profile_icon1, _ = ProfileIcon.objects.get_or_create(
            profile_id='test_1',
            defaults={'image_path': 'profileicon/1.png'}
        )
        profile_icon2, _ = ProfileIcon.objects.get_or_create(
            profile_id='test_2', 
            defaults={'image_path': 'profileicon/2.png'}
        )
        
        # Create summoners
        summoner1, _ = Summoner.objects.get_or_create(
            puuid='test_summoner_1',
            defaults={
                'game_name': 'TestPlayer1',
                'tag_line': 'NA1',
                'summoner_level': 45,
                'profile_icon': profile_icon1
            }
        )
        summoner2, _ = Summoner.objects.get_or_create(
            puuid='test_summoner_2',
            defaults={
                'game_name': 'TestPlayer2',
                'tag_line': 'NA1', 
                'summoner_level': 32,
                'profile_icon': profile_icon2
            }
        )
        
        # Create champions
        champion1, _ = Champion.objects.get_or_create(
            champion_id='TestAatrox',
            defaults={
                'name': 'Aatrox',
                'title': 'The Darkin Blade',
                'image_path': 'Aatrox.png'
            }
        )
        champion2, _ = Champion.objects.get_or_create(
            champion_id='TestJinx',
            defaults={
                'name': 'Jinx',
                'title': 'The Loose Cannon',
                'image_path': 'Jinx.png'
            }
        )
        
        # Create summoner spells
        spell1, _ = SummonerSpell.objects.get_or_create(
            spell_id=4,
            defaults={
                'name': 'Flash',
                'image_path': 'SummonerFlash.png'
            }
        )
        spell2, _ = SummonerSpell.objects.get_or_create(
            spell_id=32,
            defaults={
                'name': 'Mark',
                'image_path': 'SummonerSnowball.png'
            }
        )
        
        # Create match
        match = Match.objects.create(
            match_id='test_enhanced_match_001',
            game_start=datetime.datetime.now(),
            game_duration=1800,
            game_mode='ARAM',
            game_version='14.17.1',
            winner=100
        )
        
        # Create participants
        participant1 = Participant.objects.create(
            match=match,
            summoner=summoner1,
            champion=champion1,
            kills=12,
            deaths=3,
            assists=15,
            creep_score=145,
            spell1=spell1,
            spell2=spell2,
            team=100,
            win=True,
            game_name='TestPlayer1'
        )
        participant2 = Participant.objects.create(
            match=match,
            summoner=summoner2,
            champion=champion2,
            kills=8,
            deaths=7,
            assists=12,
            creep_score=132,
            spell1=spell1,
            spell2=spell2,
            team=200,
            win=False,
            game_name='TestPlayer2'
        )
        
        print("✓ Test data created successfully")
        
        # Test data availability
        from match_history.views import _get_match_data
        from django.core.paginator import Paginator
        
        matches_queryset = Match.objects.filter(participants__summoner=summoner1).prefetch_related(
            'participants__summoner', 'participants__champion', 'participants__summoner__profile_icon'
        )
        paginator = Paginator(matches_queryset, 10)
        page_obj = paginator.get_page(1)
        match_data = _get_match_data(summoner1, page_obj)
        
        if len(match_data) == 1:
            print("✓ Match data retrieved successfully")
            
            match, main_participant, blue_team, red_team, main_stats = match_data[0]
            
            # Test participant data
            all_participants = blue_team + red_team
            for participant in all_participants:
                assert participant.kills is not None, "Kills data missing"
                assert participant.deaths is not None, "Deaths data missing"
                assert participant.assists is not None, "Assists data missing"
                assert participant.creep_score is not None, "Creep score missing"
                assert participant.summoner.summoner_level is not None, "Summoner level missing"
                assert participant.win is not None, "Win status missing"
                
            print("✓ All participant data is available")
            
            # Test profile icon availability
            for participant in all_participants:
                if participant.summoner.profile_icon:
                    assert participant.summoner.profile_icon.get_url() is not None, "Profile icon URL missing"
                    
            print("✓ Profile icon data is available")
            
            # Test template rendering (simplified)
            template_content = """
            {% for participant in participants %}
                <div class="participant-entry">
                    <span>{{participant.game_name}}</span>
                    <span>{{participant.kills}}/{{participant.deaths}}/{{participant.assists}}</span>
                    <span>Lv{{participant.summoner.summoner_level}}</span>
                    <span>{{participant.creep_score}}cs</span>
                    <span class="{% if participant.win %}win{% else %}loss{% endif %}">{{participant.win}}</span>
                </div>
            {% endfor %}
            """
            
            template = Template(template_content)
            context = Context({'participants': all_participants})
            rendered = template.render(context)
            
            # Check that rendered content contains expected data
            assert 'TestPlayer1' in rendered, "Player name not rendered"
            assert '12/3/15' in rendered, "KDA not rendered correctly"
            assert 'Lv45' in rendered, "Level not rendered correctly"
            assert '145cs' in rendered, "CS not rendered correctly"
            
            print("✓ Template rendering works correctly")
            print("✓ All tests passed!")
            
        else:
            print("✗ Failed to retrieve match data")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test data
        try:
            Match.objects.filter(match_id__startswith='test_').delete()
            Summoner.objects.filter(puuid__startswith='test_').delete()
            Champion.objects.filter(champion_id__startswith='Test').delete()
            ProfileIcon.objects.filter(profile_id__startswith='test_').delete()
            print("✓ Test data cleaned up")
        except:
            pass
    
    return True

if __name__ == '__main__':
    success = test_enhanced_match_cards()
    sys.exit(0 if success else 1)