#!/usr/bin/env python
"""
Test script to verify the enhanced match statistics implementation
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/workspace')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

# Import models to test
try:
    from match_history.models import Participant, Match, Summoner, Champion, SummonerSpell
    print("✓ Successfully imported models")
except ImportError as e:
    print(f"✗ Failed to import models: {e}")
    sys.exit(1)

# Test model field access
try:
    # Check if new fields exist on the Participant model
    participant_fields = [field.name for field in Participant._meta.get_fields()]
    
    expected_new_fields = [
        'total_damage_dealt_to_champions',
        'total_damage_taken',
        'magic_damage_dealt_to_champions',
        'physical_damage_dealt_to_champions',
        'true_damage_dealt_to_champions',
        'damage_self_mitigated',
        'vision_score',
        'wards_placed',
        'wards_killed',
        'vision_wards_bought_in_game',
        'turret_kills',
        'inhibitor_kills',
        'dragon_kills',
        'baron_kills',
        'gold_earned',
        'gold_spent',
        'total_heal',
        'total_units_healed'
    ]
    
    missing_fields = []
    for field in expected_new_fields:
        if field not in participant_fields:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"✗ Missing fields in Participant model: {missing_fields}")
    else:
        print("✓ All expected fields found in Participant model")
        
except Exception as e:
    print(f"✗ Error checking model fields: {e}")

# Test model methods
try:
    # Check if new methods exist
    participant_methods = [method for method in dir(Participant) if not method.startswith('_')]
    
    expected_methods = [
        'get_damage_share_percentage',
        'get_kill_participation_percentage',
        'get_kda_ratio',
        'get_gold_efficiency'
    ]
    
    missing_methods = []
    for method in expected_methods:
        if method not in participant_methods:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"✗ Missing methods in Participant model: {missing_methods}")
    else:
        print("✓ All expected methods found in Participant model")
        
except Exception as e:
    print(f"✗ Error checking model methods: {e}")

# Test views import
try:
    from match_history.views import _get_match_data, _get_new_match_data, _get_match_queryset
    print("✓ Successfully imported view functions")
except ImportError as e:
    print(f"✗ Failed to import view functions: {e}")

# Test populate_data import
try:
    from match_history.util.populate_data import MatchManager
    print("✓ Successfully imported populate_data functions")
except ImportError as e:
    print(f"✗ Failed to import populate_data functions: {e}")

print("\nImplementation verification complete!")