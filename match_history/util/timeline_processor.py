from match_history.models import Match, TimelineEvent, Participant

def process_match_timeline(match_id, timeline_data):
    """
    Process timeline data from the Riot API and create TimelineEvent objects.
    
    Args:
        match_id (str): The match ID
        timeline_data (dict): Timeline data from Riot API
    
    Returns:
        bool: True if timeline was processed successfully, False otherwise
    """
    try:
        match = Match.objects.get(match_id=match_id)
        
        # Clear existing timeline events for this match
        TimelineEvent.objects.filter(match=match).delete()
        
        # Process timeline frames
        if 'info' in timeline_data and 'frames' in timeline_data['info']:
            frames = timeline_data['info']['frames']
            
            for frame in frames:
                timestamp = frame.get('timestamp', 0) // 1000  # Convert from milliseconds to seconds
                
                # Process champion kills
                if 'events' in frame:
                    for event in frame['events']:
                        event_type = event.get('type')
                        
                        if event_type == 'CHAMPION_KILL':
                            process_champion_kill(match, event, timestamp)
                        elif event_type == 'BUILDING_KILL':
                            process_building_kill(match, event, timestamp)
                        elif event_type == 'ELITE_MONSTER_KILL':
                            process_monster_kill(match, event, timestamp)
                        elif event_type == 'ITEM_PURCHASED' and event.get('itemId') in [3340, 3363, 3364]:  # Wards
                            process_item_purchase(match, event, timestamp)
                        elif event_type == 'LEVEL_UP' and event.get('level') % 3 == 0:  # Every 3 levels
                            process_level_up(match, event, timestamp)
            
            # Mark match as having timeline data
            match.has_timeline = True
            match.save()
            
            return True
    except Exception as e:
        print(f"Error processing timeline for match {match_id}: {e}")
        return False
    
    return False

def process_champion_kill(match, event, timestamp):
    """Process a champion kill event"""
    try:
        killer_id = event.get('killerId')
        victim_id = event.get('victimId')
        assisting_ids = event.get('assistingParticipantIds', [])
        
        # Get participants
        try:
            killer = Participant.objects.get(match=match, summoner__puuid=killer_id) if killer_id else None
            victim = Participant.objects.get(match=match, summoner__puuid=victim_id) if victim_id else None
            
            # Create kill event
            kill_event = TimelineEvent.objects.create(
                match=match,
                event_type='KILL',
                timestamp=timestamp,
                description=f"{killer.game_name if killer else 'Unknown'} killed {victim.game_name if victim else 'Unknown'}",
                position_x=event.get('position', {}).get('x'),
                position_y=event.get('position', {}).get('y'),
                additional_data={
                    'killer_champion': killer.champion.name if killer else 'Unknown',
                    'victim_champion': victim.champion.name if victim else 'Unknown',
                }
            )
            
            # Add participants involved
            if killer:
                kill_event.participants_involved.add(killer)
            if victim:
                kill_event.participants_involved.add(victim)
            
            # Create assist events
            for assist_id in assisting_ids:
                try:
                    assistant = Participant.objects.get(match=match, summoner__puuid=assist_id)
                    assist_event = TimelineEvent.objects.create(
                        match=match,
                        event_type='ASSIST',
                        timestamp=timestamp,
                        description=f"{assistant.game_name} assisted in killing {victim.game_name if victim else 'Unknown'}",
                        position_x=event.get('position', {}).get('x'),
                        position_y=event.get('position', {}).get('y')
                    )
                    assist_event.participants_involved.add(assistant)
                    if victim:
                        assist_event.participants_involved.add(victim)
                except Participant.DoesNotExist:
                    pass
            
            # Create death event
            if victim:
                death_event = TimelineEvent.objects.create(
                    match=match,
                    event_type='DEATH',
                    timestamp=timestamp,
                    description=f"{victim.game_name} was killed by {killer.game_name if killer else 'Unknown'}",
                    position_x=event.get('position', {}).get('x'),
                    position_y=event.get('position', {}).get('y')
                )
                death_event.participants_involved.add(victim)
                if killer:
                    death_event.participants_involved.add(killer)
        
        except Participant.DoesNotExist:
            pass
    
    except Exception as e:
        print(f"Error processing champion kill: {e}")

def process_building_kill(match, event, timestamp):
    """Process a building kill event"""
    try:
        killer_id = event.get('killerId')
        building_type = event.get('buildingType', 'Unknown')
        lane = event.get('laneType', 'Unknown')
        team_id = event.get('teamId')
        
        # Get killer participant
        try:
            killer = Participant.objects.get(match=match, summoner__puuid=killer_id) if killer_id else None
            
            # Create building kill event
            building_event = TimelineEvent.objects.create(
                match=match,
                event_type='BUILDING',
                timestamp=timestamp,
                description=f"{killer.game_name if killer else 'Minions'} destroyed a {building_type} in {lane}",
                position_x=event.get('position', {}).get('x'),
                position_y=event.get('position', {}).get('y'),
                additional_data={
                    'building_type': building_type,
                    'lane': lane,
                    'team_id': team_id
                }
            )
            
            # Add participant involved
            if killer:
                building_event.participants_involved.add(killer)
        
        except Participant.DoesNotExist:
            pass
    
    except Exception as e:
        print(f"Error processing building kill: {e}")

def process_monster_kill(match, event, timestamp):
    """Process an elite monster kill event"""
    try:
        killer_id = event.get('killerId')
        monster_type = event.get('monsterType', 'Unknown')
        monster_subtype = event.get('monsterSubType', '')
        
        # Get killer participant
        try:
            killer = Participant.objects.get(match=match, summoner__puuid=killer_id) if killer_id else None
            
            # Create monster kill event
            monster_event = TimelineEvent.objects.create(
                match=match,
                event_type='OBJECTIVE',
                timestamp=timestamp,
                description=f"{killer.game_name if killer else 'Unknown'} killed {monster_subtype if monster_subtype else monster_type}",
                position_x=event.get('position', {}).get('x'),
                position_y=event.get('position', {}).get('y'),
                additional_data={
                    'monster_type': monster_type,
                    'monster_subtype': monster_subtype
                }
            )
            
            # Add participant involved
            if killer:
                monster_event.participants_involved.add(killer)
        
        except Participant.DoesNotExist:
            pass
    
    except Exception as e:
        print(f"Error processing monster kill: {e}")

def process_item_purchase(match, event, timestamp):
    """Process an item purchase event"""
    try:
        participant_id = event.get('participantId')
        item_id = event.get('itemId')
        
        # Get participant
        try:
            participant = Participant.objects.get(match=match, summoner__puuid=participant_id) if participant_id else None
            
            # Create item purchase event
            item_event = TimelineEvent.objects.create(
                match=match,
                event_type='ITEM_PURCHASED',
                timestamp=timestamp,
                description=f"{participant.game_name if participant else 'Unknown'} purchased ward item",
                additional_data={
                    'item_id': item_id
                }
            )
            
            # Add participant involved
            if participant:
                item_event.participants_involved.add(participant)
        
        except Participant.DoesNotExist:
            pass
    
    except Exception as e:
        print(f"Error processing item purchase: {e}")

def process_level_up(match, event, timestamp):
    """Process a level up event"""
    try:
        participant_id = event.get('participantId')
        level = event.get('level')
        
        # Get participant
        try:
            participant = Participant.objects.get(match=match, summoner__puuid=participant_id) if participant_id else None
            
            # Create level up event
            level_event = TimelineEvent.objects.create(
                match=match,
                event_type='LEVEL_UP',
                timestamp=timestamp,
                description=f"{participant.game_name if participant else 'Unknown'} reached level {level}",
                additional_data={
                    'level': level
                }
            )
            
            # Add participant involved
            if participant:
                level_event.participants_involved.add(participant)
        
        except Participant.DoesNotExist:
            pass
    
    except Exception as e:
        print(f"Error processing level up: {e}")