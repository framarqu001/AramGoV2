# Enhanced Match Data Query and Processing

This document outlines the enhancements made to the match data query and processing system to include expanded statistics for damage, vision, objectives, and calculated performance metrics.

## Overview

The enhancement adds comprehensive match statistics to the Participant model and updates the data processing pipeline to capture, store, and calculate advanced performance metrics including damage share and kill participation percentages.

## Changes Made

### 1. Participant Model Enhancements (`match_history/models.py`)

#### New Fields Added:
- **Damage Statistics:**
  - `total_damage_dealt_to_champions` - Total damage dealt to enemy champions
  - `total_damage_taken` - Total damage taken from all sources
  - `magic_damage_dealt_to_champions` - Magic damage dealt to champions
  - `physical_damage_dealt_to_champions` - Physical damage dealt to champions
  - `true_damage_dealt_to_champions` - True damage dealt to champions
  - `damage_self_mitigated` - Damage mitigated through shields/resistances

- **Vision Statistics:**
  - `vision_score` - Overall vision score
  - `wards_placed` - Number of wards placed
  - `wards_killed` - Number of enemy wards destroyed
  - `vision_wards_bought_in_game` - Control wards purchased

- **Objective Statistics:**
  - `turret_kills` - Number of turrets destroyed
  - `inhibitor_kills` - Number of inhibitors destroyed
  - `dragon_kills` - Number of dragons killed
  - `baron_kills` - Number of barons killed

- **Economy Statistics:**
  - `gold_earned` - Total gold earned during the match
  - `gold_spent` - Total gold spent on items

- **Healing Statistics:**
  - `total_heal` - Total healing provided
  - `total_units_healed` - Number of units healed

#### New Methods Added:
- `get_damage_share_percentage(team_participants=None)` - Calculates damage share within team
- `get_kill_participation_percentage(team_participants=None)` - Calculates kill participation within team
- `get_kda_ratio()` - Calculates KDA ratio with proper zero-death handling
- `get_gold_efficiency()` - Calculates gold spending efficiency

### 2. Data Population Updates (`match_history/util/populate_data.py`)

Enhanced the `_create_participants` method to extract and store additional statistics from the Riot API response:
- Added extraction of all new damage, vision, objective, economy, and healing statistics
- Implemented safe extraction using `.get()` method with default values to handle missing data
- Maintained backward compatibility with existing data processing

### 3. View Function Enhancements (`match_history/views.py`)

#### Updated Functions:
- **`_get_match_data(summoner, page_obj)`:**
  - Added calculation of damage share and kill participation percentages
  - Added gold per minute and damage per minute calculations
  - Optimized team participant queries to avoid N+1 database queries
  - Enhanced main_stats dictionary with new metrics

- **`_get_new_match_data(summoner)`:**
  - Applied same enhancements as `_get_match_data` for consistency
  - Maintained real-time update functionality

#### New Statistics Available in Template Context:
- `damage_share` - Percentage of team's total damage
- `kill_participation` - Percentage participation in team kills
- `gold_per_min` - Gold earned per minute
- `damage_per_min` - Damage dealt per minute
- `vision_score` - Vision score value
- `total_damage` - Total damage dealt to champions
- `gold_earned` - Total gold earned
- `wards_placed` - Wards placed count
- `wards_killed` - Enemy wards destroyed count

### 4. Database Migrations

#### Created Migration Files:
- **`0001_initial.py`** - Initial database schema
- **`0002_add_enhanced_participant_stats.py`** - Adds all new Participant model fields

#### Migration Features:
- All new fields have `default=0` to handle existing records
- Proper field types (IntegerField) for all statistics
- Maintains referential integrity

### 5. Enhanced Testing (`match_history/tests.py`)

#### New Test Classes:
- **`EnhancedParticipantStatsTest`** - Comprehensive testing of new functionality
  - Tests damage share percentage calculations
  - Tests kill participation percentage calculations
  - Tests KDA ratio calculations
  - Tests gold efficiency calculations
  - Tests zero division handling for edge cases

#### Test Coverage:
- Model method functionality
- Edge case handling (zero values, division by zero)
- Calculation accuracy verification
- Database relationship integrity

## Performance Optimizations

### Query Optimization:
- **Team Participant Caching:** Modified model methods to accept pre-fetched team participants to avoid N+1 queries
- **Efficient Data Organization:** Views now organize participants by team during initial processing
- **Maintained Prefetch Patterns:** Existing `prefetch_related` optimizations preserved

### Calculation Efficiency:
- **Single Pass Processing:** Team statistics calculated once per match
- **Optimized Method Signatures:** Model methods accept optional team participant lists
- **Reduced Database Queries:** Team filtering done in memory when possible

## Usage Examples

### Accessing New Statistics in Templates:
```python
# In views.py context
main_stats = {
    "damage_share": f"{damage_share:.1f}%",
    "kill_participation": f"{kill_participation:.1f}%",
    "gold_per_min": f"{gold_per_min:.0f}",
    "damage_per_min": f"{damage_per_min:.0f}",
    "vision_score": main_participant.vision_score,
    "total_damage": main_participant.total_damage_dealt_to_champions,
    # ... other statistics
}
```

### Using Model Methods:
```python
# Calculate damage share for a participant
damage_share = participant.get_damage_share_percentage()

# Calculate with pre-fetched team data (more efficient)
team_participants = match.participants.filter(team=participant.team)
damage_share = participant.get_damage_share_percentage(team_participants)

# Calculate kill participation
kill_participation = participant.get_kill_participation_percentage()

# Get KDA ratio
kda = participant.get_kda_ratio()

# Get gold efficiency
gold_efficiency = participant.get_gold_efficiency()
```

## Migration Instructions

1. **Apply Migrations:**
   ```bash
   python manage.py migrate match_history
   ```

2. **Verify Database Schema:**
   ```bash
   python manage.py dbshell
   \d match_history_participant  # PostgreSQL
   # or
   .schema match_history_participant  # SQLite
   ```

3. **Run Tests:**
   ```bash
   python manage.py test match_history.tests.EnhancedParticipantStatsTest
   ```

## Backward Compatibility

- All existing functionality remains unchanged
- New fields have default values to handle existing records
- Existing templates will continue to work without modification
- API responses maintain existing structure while adding new data

## Future Enhancements

### Potential Additions:
- **Damage Breakdown Charts:** Visual representation of damage types
- **Vision Heatmaps:** Ward placement and vision control analysis
- **Objective Timeline:** Chronological objective capture tracking
- **Performance Trends:** Historical performance metric tracking
- **Team Comparison:** Cross-team statistical comparisons

### Performance Monitoring:
- Monitor query performance with expanded data set
- Consider database indexing for frequently queried fields
- Evaluate caching strategies for calculated statistics

## Troubleshooting

### Common Issues:
1. **Migration Errors:** Ensure database has proper permissions for schema changes
2. **Missing Statistics:** Verify Riot API response contains expected fields
3. **Performance Issues:** Check that prefetch_related patterns are maintained
4. **Calculation Errors:** Verify team participant filtering logic

### Debug Commands:
```bash
# Check model fields
python manage.py shell -c "from match_history.models import Participant; print([f.name for f in Participant._meta.fields])"

# Test calculations
python manage.py shell -c "from match_history.models import Participant; p = Participant.objects.first(); print(p.get_damage_share_percentage())"

# Verify migrations
python manage.py showmigrations match_history
```

## Conclusion

The enhanced match data query and processing system provides comprehensive statistics while maintaining performance and backward compatibility. The implementation follows Django best practices and includes thorough testing to ensure reliability.