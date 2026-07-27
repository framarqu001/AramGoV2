from django.core.cache import cache
from .models import Match, Participant

def expanded_match_data(request):
    """
    Context processor that provides expanded match data to all templates.
    This allows templates to access expanded match statistics without
    having to pass them explicitly in each view.
    """
    # If we're on a match detail page, we can try to get the match ID from the URL
    match_id = request.GET.get('match_id')
    
    if not match_id:
        # No match ID in the URL, return empty context
        return {'expanded_match_data': {}}
    
    # Try to get the expanded match data from cache
    cache_key = f'expanded_match_data_context_{match_id}'
    expanded_data = cache.get(cache_key)
    
    if expanded_data:
        return {'expanded_match_data': expanded_data}
    
    # If not in cache, try to get the match from the database
    try:
        match = Match.objects.get(match_id=match_id)
        
        # Get all participants for this match
        participants = Participant.objects.filter(match=match).select_related('summoner', 'champion')
        
        # Prepare expanded data
        expanded_data = {
            'match': {
                'id': match.match_id,
                'duration': match.get_duration(),
                'game_mode': match.game_mode,
                'game_version': match.game_version,
                'winner': match.winner,
                'blue_team_objectives': match.get_team_objectives(Match.BLUE_TEAM),
                'red_team_objectives': match.get_team_objectives(Match.RED_TEAM),
            },
            'participants': {}
        }
        
        # Add participant data
        for participant in participants:
            participant_data = {
                'summoner_name': participant.game_name,
                'champion': participant.champion.name,
                'team': participant.team,
                'win': participant.win,
                'kda': {
                    'kills': participant.kills,
                    'deaths': participant.deaths,
                    'assists': participant.assists,
                },
                'damage': participant.get_damage_stats() if hasattr(participant, 'get_damage_stats') else {},
                'gold': participant.get_gold_stats() if hasattr(participant, 'get_gold_stats') else {},
                'vision': participant.get_vision_stats() if hasattr(participant, 'get_vision_stats') else {},
            }
            expanded_data['participants'][participant.summoner.puuid] = participant_data
        
        # Cache the expanded data
        cache.set(cache_key, expanded_data, timeout=3600)  # Cache for 1 hour
        
        return {'expanded_match_data': expanded_data}
    except Match.DoesNotExist:
        # Match not found, return empty context
        return {'expanded_match_data': {}}