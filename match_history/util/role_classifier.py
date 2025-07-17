"""
Utility functions for classifying champion roles in ARAM.
"""
from match_history.models import Participant, Champion

# Champion role classifications
# These are simplified for ARAM and may not match official classifications
TANK_CHAMPIONS = [
    'Alistar', 'Amumu', 'Braum', 'Cho\'Gath', 'Dr. Mundo', 'Galio', 'Leona', 
    'Malphite', 'Maokai', 'Nautilus', 'Ornn', 'Rammus', 'Sejuani', 'Shen', 
    'Sion', 'Tahm Kench', 'Zac'
]

BRUISER_CHAMPIONS = [
    'Aatrox', 'Camille', 'Darius', 'Fiora', 'Garen', 'Gnar', 'Hecarim', 
    'Illaoi', 'Irelia', 'Jax', 'Kled', 'Lee Sin', 'Mordekaiser', 'Nasus', 
    'Olaf', 'Pantheon', 'Renekton', 'Rengar', 'Riven', 'Sett', 'Shyvana', 
    'Trundle', 'Udyr', 'Vi', 'Volibear', 'Warwick', 'Wukong', 'Xin Zhao', 
    'Yorick'
]

MAGE_CHAMPIONS = [
    'Ahri', 'Anivia', 'Annie', 'Aurelion Sol', 'Azir', 'Brand', 'Cassiopeia', 
    'Fiddlesticks', 'Heimerdinger', 'Karma', 'Karthus', 'Kassadin', 'Kennen', 
    'LeBlanc', 'Lissandra', 'Lux', 'Malzahar', 'Neeko', 'Orianna', 'Ryze', 
    'Seraphine', 'Swain', 'Sylas', 'Syndra', 'Taliyah', 'Twisted Fate', 
    'Veigar', 'Vel\'Koz', 'Viktor', 'Vladimir', 'Xerath', 'Ziggs', 'Zilean', 
    'Zoe', 'Zyra'
]

MARKSMAN_CHAMPIONS = [
    'Aphelios', 'Ashe', 'Caitlyn', 'Corki', 'Draven', 'Ezreal', 'Graves', 
    'Jhin', 'Jinx', 'Kai\'Sa', 'Kalista', 'Kindred', 'Kog\'Maw', 'Lucian', 
    'Miss Fortune', 'Samira', 'Senna', 'Sivir', 'Tristana', 'Twitch', 'Varus', 
    'Vayne', 'Xayah'
]

SUPPORT_CHAMPIONS = [
    'Bard', 'Janna', 'Lulu', 'Nami', 'Pyke', 'Rakan', 'Sona', 'Soraka', 
    'Taric', 'Thresh', 'Yuumi'
]

ASSASSIN_CHAMPIONS = [
    'Akali', 'Diana', 'Ekko', 'Evelynn', 'Fizz', 'Katarina', 'Kayn', 'Kha\'Zix', 
    'Nocturne', 'Qiyana', 'Shaco', 'Talon', 'Zed'
]

def determine_role(champion_name):
    """
    Determine the role of a champion based on their name.
    
    Args:
        champion_name (str): The name of the champion
        
    Returns:
        str: The role of the champion (one of the Participant.ROLE_CHOICES)
    """
    if champion_name in TANK_CHAMPIONS:
        return Participant.TANK
    elif champion_name in BRUISER_CHAMPIONS:
        return Participant.BRUISER
    elif champion_name in MAGE_CHAMPIONS:
        return Participant.MAGE
    elif champion_name in MARKSMAN_CHAMPIONS:
        return Participant.MARKSMAN
    elif champion_name in SUPPORT_CHAMPIONS:
        return Participant.SUPPORT
    elif champion_name in ASSASSIN_CHAMPIONS:
        return Participant.ASSASSIN
    else:
        # Default to MAGE if unknown
        return Participant.MAGE

def assign_roles_to_participants(match):
    """
    Assign roles to all participants in a match.
    
    Args:
        match: A Match object
        
    Returns:
        None
    """
    for participant in match.participants.all():
        if not participant.role:
            participant.role = determine_role(participant.champion.name)
            participant.save()