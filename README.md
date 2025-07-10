# AramGo - League of Legends ARAM Match History

AramGo is a Django application that integrates with the Riot Games API to track and analyze ARAM (All Random All Mid) matches in League of Legends.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Riot Games API Key

### Getting a Riot Games API Key

1. Visit the [Riot Developer Portal](https://developer.riotgames.com/)
2. Create an account or log in
3. Register a new application
4. Generate a Development API Key

Note: Development API keys expire after 24 hours. For production use, you'll need to apply for a Production API Key.

### Environment Configuration

1. Copy the sample environment file:
   ```
   cp .env-sample .env
   ```

2. Edit the `.env` file and add your Riot API key:
   ```
   RIOT_API_KEY=RGAPI-your-api-key-here
   ```

3. Update other environment variables as needed.

### Running with Docker

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. The application should now be running at http://localhost:8000

## API Integration

The application integrates with the following Riot Games API endpoints:

- **Account-V1**: For retrieving account information by Riot ID
- **Summoner-V4**: For retrieving summoner details
- **Match-V5**: For retrieving match history and details

### Using the API Client

The application includes a dedicated Riot API client that handles authentication, rate limiting, and error handling:

```python
from AramGoV2.util.riot_api import RiotAPIClient

# Initialize the client
client = RiotAPIClient(region='na')

# Get summoner information
summoner = client.get_summoner_by_riot_id('SummonerName', 'NA1')

# Get match history
matches = client.get_match_list(summoner['puuid'])

# Get match details
match_details = client.get_match_details(matches[0])
```

## Features

- Summoner profile lookup
- Match history tracking
- Champion statistics
- Win rate analysis
- Item build tracking

## Error Handling

The application includes comprehensive error handling for API requests:

- Rate limit management
- API key validation
- Network error handling
- Data validation

## Testing

Run the tests with:

```
python manage.py test
```

## License

This project is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.