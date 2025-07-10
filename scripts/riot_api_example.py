#!/usr/bin/env python
"""
Example script demonstrating how to use the Riot API client.

This script shows how to:
1. Initialize the Riot API client
2. Fetch summoner information
3. Get match history
4. Get match details
5. Handle errors

Usage:
    python riot_api_example.py <summoner_name> <tag_line>

Example:
    python riot_api_example.py "Riot Zenith" "NA1"
"""
import os
import sys
import django
import json
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AramGoV2.settings')
django.setup()

from AramGoV2.util.riot_api import RiotAPIClient
from riotwatcher import ApiError


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def main():
    """Main function to demonstrate the Riot API client."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <summoner_name> <tag_line>")
        print(f"Example: {sys.argv[0]} \"Riot Zenith\" \"NA1\"")
        sys.exit(1)
    
    summoner_name = sys.argv[1]
    tag_line = sys.argv[2]
    
    print(f"Looking up summoner: {summoner_name}#{tag_line}")
    
    try:
        # Initialize the client
        client = RiotAPIClient(region='na')
        
        # Get summoner information
        print("\n1. Fetching summoner information...")
        summoner = client.get_summoner_by_riot_id(summoner_name, tag_line)
        print(f"Found summoner: {summoner.get('name')} (Level {summoner.get('summonerLevel')})")
        
        # Get match history
        print("\n2. Fetching recent matches...")
        matches = client.get_match_list(summoner['puuid'], count=5)
        print(f"Found {len(matches)} recent matches")
        
        if matches:
            # Get match details for the most recent match
            print("\n3. Fetching details for the most recent match...")
            match_id = matches[0]
            match_details = client.get_match_details(match_id)
            
            # Extract and display some basic information
            game_mode = match_details['info']['gameMode']
            game_duration = match_details['info']['gameDuration']
            game_creation = datetime.fromtimestamp(match_details['info']['gameCreation'] / 1000)
            
            print(f"Match ID: {match_id}")
            print(f"Game Mode: {game_mode}")
            print(f"Duration: {game_duration // 60}m {game_duration % 60}s")
            print(f"Date: {game_creation.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Find the summoner in the participants list
            for participant in match_details['info']['participants']:
                if participant['puuid'] == summoner['puuid']:
                    champion = participant['championName']
                    kills = participant['kills']
                    deaths = participant['deaths']
                    assists = participant['assists']
                    win = participant['win']
                    
                    print(f"\nYou played: {champion}")
                    print(f"KDA: {kills}/{deaths}/{assists}")
                    print(f"Result: {'Victory' if win else 'Defeat'}")
                    break
    
    except ApiError as e:
        status = e.response.status_code
        if status == 429:
            print("Error: Rate limit exceeded. Please try again later.")
        elif status == 404:
            print(f"Error: Summoner '{summoner_name}#{tag_line}' not found.")
        elif status == 403:
            print("Error: API key invalid or expired.")
        else:
            print(f"API Error ({status}): {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()