# Riot API Integration Extension - Participant Stats

This document describes the implementation of extended participant statistics for the Riot Games API integration in the AramGoV2 project.

## Overview

The extension adds KDA ratio and damage statistics to participant data by integrating with the Riot Games Match Timeline API. This provides more detailed statistics for match analysis while maintaining backward compatibility with existing functionality.

## Changes Made

### 1. Database Schema Extensions (`match_history/models.py`)

Added new fields to the `Participant` model:

- `kda_ratio` (DecimalField): Calculated as (kills + assists) / max(deaths, 1)
- `total_damage_dealt` (BigIntegerField): Total damage dealt to all targets
- `damage_to_champions` (BigIntegerField): Total damage dealt to enemy champions  
- `damage_taken` (BigIntegerField): Total damage taken from all sources

All fields are nullable and optional for backward compatibility.

#### New Methods Added:
- `calculate_kda_ratio()`: Calculates KDA ratio dynamically
- `get_kda_ratio()`: Returns stored KDA ratio or calculates if not available

### 2. API Integration Enhancement (`match_history/util/populate_data.py`)

#### New Methods:
- `_get_match_timeline(match_id)`: Fetches timeline data from Riot API
- `_extract_damage_stats_from_timeline(timeline_data, participant_id)`: Extracts damage stats from timeline
- `_calculate_kda_ratio(kills, deaths, assists)`: Calculates KDA with proper error handling

#### Enhanced Methods:
- `_create_participants()`: Now fetches timeline data and extracts extended statistics
- `process_matches()`: Improved error handling for API failures
- `last_20()`: Updated with same error handling improvements

#### Error Handling Improvements:
- Replaced print statements with proper logging
- Timeline API failures don't break match processing
- Graceful degradation when timeline data is unavailable
- Comprehensive error logging with context

### 3. Database Migration (`match_history/migrations/0001_add_participant_extended_stats.py`)

Created migration to add new fields to existing Participant table:
- All fields are nullable for backward compatibility
- Includes helpful field descriptions
- Safe to apply to existing databases

### 4. Enhanced Testing (`match_history/tests.py`)

#### New Test Classes:
- `MatchManagerTest`: Comprehensive tests for new MatchManager functionality

#### New Test Methods:
- KDA ratio calculation tests (including edge cases)
- Timeline API integration tests
- Error handling tests
- Extended statistics field validation tests
- Mock API response testing

## API Integration Details

### Timeline API Usage

The extension integrates with the Riot Games Match Timeline API endpoint:
```
GET /lol/match/v5/matches/{matchId}/timeline
```

### Data Flow

1. **Match Processing**: When processing matches, the system now:
   - Fetches basic match data (existing functionality)
   - Attempts to fetch timeline data (new functionality)
   - Extracts damage statistics from timeline if available
   - Falls back to basic match data if timeline unavailable
   - Calculates and stores KDA ratio

2. **Error Handling**: 
   - Timeline API failures are logged but don't stop match processing
   - Malformed timeline data is handled gracefully
   - API rate limiting is respected

3. **Data Priority**:
   - Timeline data is preferred for damage statistics (more accurate)
   - Falls back to match data if timeline unavailable
   - KDA ratio is always calculated from basic kill/death/assist data

## Usage Examples

### Accessing Extended Statistics

```python
# Get a participant
participant = Participant.objects.get(id=1)

# Access new fields
kda_ratio = participant.get_kda_ratio()  # Returns stored or calculated KDA
total_damage = participant.total_damage_dealt
damage_to_champs = participant.damage_to_champions
damage_taken = participant.damage_taken

# Calculate KDA dynamically
calculated_kda = participant.calculate_kda_ratio()
```

### Processing Matches with Extended Stats

```python
from match_history.util.populate_data import MatchManager

# Create match manager
match_manager = MatchManager("americas", "na1", summoner)

# Process matches (now includes timeline data fetching)
match_manager.process_matches()

# The system will automatically:
# 1. Fetch match details
# 2. Attempt to fetch timeline data
# 3. Extract and store extended statistics
# 4. Handle any API errors gracefully
```

## Configuration and Deployment

### Database Migration

Run the migration to add new fields:
```bash
python manage.py migrate match_history
```

### Logging Configuration

The extension uses Python's logging module. Configure logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'riot_api.log',
        },
    },
    'loggers': {
        'match_history.util.populate_data': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Performance Considerations

### API Rate Limiting
- Timeline API has separate rate limits from match details API
- System respects rate limits and handles 429 responses
- Failed timeline requests don't retry to avoid rate limit issues

### Database Performance
- New fields are indexed appropriately for query performance
- BigInteger fields accommodate large damage values
- Decimal field for KDA ratio provides precise calculations

### Memory Usage
- Timeline data is processed immediately and not stored in memory
- Large timeline responses are handled efficiently
- Garbage collection occurs after each match processing

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test match_history

# Run specific test classes
python manage.py test match_history.tests.MatchManagerTest
python manage.py test match_history.tests.MatchParticipantTest
```

### Test Coverage

The test suite covers:
- KDA ratio calculations (including edge cases)
- Timeline API integration
- Error handling scenarios
- Database field validation
- Backward compatibility
- Mock API responses

## Backward Compatibility

### Existing Data
- Existing participants will have null values for new fields
- System continues to work with existing data
- New fields are optional and don't break existing queries

### API Compatibility
- Existing match processing continues to work
- Timeline API integration is additive, not replacing existing functionality
- Error handling ensures system stability

## Troubleshooting

### Common Issues

1. **Timeline API Unavailable**
   - System logs warning and continues processing
   - Damage statistics will be null or from basic match data
   - KDA ratio still calculated from basic stats

2. **API Rate Limiting**
   - System respects rate limits
   - Failed requests are logged
   - Processing continues with available data

3. **Database Migration Issues**
   - Ensure database backup before migration
   - Migration is designed to be safe for existing data
   - All new fields are nullable

### Monitoring

Monitor these log messages:
- `Timeline data available for match {match_id}` - Success
- `Timeline data not available for match {match_id}` - Expected fallback
- `Error fetching timeline data for match ID {match_id}` - API issues
- `Successfully processed new match {match_id}` - Processing success

## Future Enhancements

Potential improvements for future versions:
1. Retry logic for failed timeline API calls
2. Batch processing for better performance
3. Caching of timeline data for frequently accessed matches
4. Additional statistics from timeline data (gold, experience, etc.)
5. Background job processing for timeline data backfilling

## Support

For issues or questions regarding this implementation:
1. Check the logs for detailed error messages
2. Verify API key permissions for timeline endpoint
3. Ensure database migration completed successfully
4. Review test cases for expected behavior examples