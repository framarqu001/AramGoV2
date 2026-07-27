"""
Utility module for champion data, including damage type mapping and team composition analysis.
"""

# Champion damage type mapping (AP: Magic damage, AD: Physical damage, HYBRID: Mixed damage)
CHAMPION_DAMAGE_TYPES = {
    # A
    "Aatrox": "AD",
    "Ahri": "AP",
    "Akali": "AP",
    "Akshan": "AD",
    "Alistar": "AP",
    "Amumu": "AP",
    "Anivia": "AP",
    "Annie": "AP",
    "Aphelios": "AD",
    "Ashe": "AD",
    "AurelionSol": "AP",
    "Azir": "AP",
    # B
    "Bard": "AP",
    "Belveth": "AD",
    "Blitzcrank": "AP",
    "Brand": "AP",
    "Braum": "AP",
    "Briar": "AD",
    # C
    "Caitlyn": "AD",
    "Camille": "AD",
    "Cassiopeia": "AP",
    "Chogath": "AP",
    "Corki": "HYBRID",
    # D
    "Darius": "AD",
    "Diana": "AP",
    "Draven": "AD",
    "DrMundo": "AP",
    # E
    "Ekko": "AP",
    "Elise": "AP",
    "Evelynn": "AP",
    "Ezreal": "HYBRID",
    # F
    "Fiddlesticks": "AP",
    "Fiora": "AD",
    "Fizz": "AP",
    # G
    "Galio": "AP",
    "Gangplank": "AD",
    "Garen": "AD",
    "Gnar": "AD",
    "Gragas": "AP",
    "Graves": "AD",
    "Gwen": "AP",
    # H
    "Hecarim": "AD",
    "Heimerdinger": "AP",
    "Hwei": "AP",
    # I
    "Illaoi": "AD",
    "Irelia": "AD",
    "Ivern": "AP",
    # J
    "Janna": "AP",
    "JarvanIV": "AD",
    "Jax": "HYBRID",
    "Jayce": "AD",
    "Jhin": "AD",
    "Jinx": "AD",
    # K
    "Kaisa": "HYBRID",
    "Kalista": "AD",
    "Karma": "AP",
    "Karthus": "AP",
    "Kassadin": "AP",
    "Katarina": "AP",
    "Kayle": "HYBRID",
    "Kayn": "AD",
    "Kennen": "AP",
    "Khazix": "AD",
    "Kindred": "AD",
    "Kled": "AD",
    "KogMaw": "HYBRID",
    "KSante": "AD",
    # L
    "Leblanc": "AP",
    "LeeSin": "AD",
    "Leona": "AP",
    "Lillia": "AP",
    "Lissandra": "AP",
    "Lucian": "AD",
    "Lulu": "AP",
    "Lux": "AP",
    # M
    "Malphite": "AP",
    "Malzahar": "AP",
    "Maokai": "AP",
    "MasterYi": "AD",
    "Milio": "AP",
    "MissFortune": "AD",
    "MonkeyKing": "AD",  # Wukong
    "Mordekaiser": "AP",
    "Morgana": "AP",
    # N
    "Naafiri": "AD",
    "Nami": "AP",
    "Nasus": "AD",
    "Nautilus": "AP",
    "Neeko": "AP",
    "Nidalee": "AP",
    "Nilah": "AD",
    "Nocturne": "AD",
    "Nunu": "AP",
    # O
    "Olaf": "AD",
    "Orianna": "AP",
    "Ornn": "AP",
    # P
    "Pantheon": "AD",
    "Poppy": "AD",
    "Pyke": "AD",
    # Q
    "Qiyana": "AD",
    "Quinn": "AD",
    # R
    "Rakan": "AP",
    "Rammus": "AP",
    "RekSai": "AD",
    "Rell": "AP",
    "Renata": "AP",
    "Renekton": "AD",
    "Rengar": "AD",
    "Riven": "AD",
    "Rumble": "AP",
    "Ryze": "AP",
    # S
    "Samira": "AD",
    "Sejuani": "AP",
    "Senna": "AD",
    "Seraphine": "AP",
    "Sett": "AD",
    "Shaco": "HYBRID",
    "Shen": "AD",
    "Shyvana": "HYBRID",
    "Singed": "AP",
    "Sion": "AD",
    "Sivir": "AD",
    "Skarner": "HYBRID",
    "Smolder": "AD",
    "Sona": "AP",
    "Soraka": "AP",
    "Swain": "AP",
    "Sylas": "AP",
    "Syndra": "AP",
    # T
    "TahmKench": "AP",
    "Taliyah": "AP",
    "Talon": "AD",
    "Taric": "AP",
    "Teemo": "AP",
    "Thresh": "AP",
    "Tristana": "AD",
    "Trundle": "AD",
    "Tryndamere": "AD",
    "TwistedFate": "AP",
    "Twitch": "AD",
    # U
    "Udyr": "HYBRID",
    "Urgot": "AD",
    # V
    "Varus": "HYBRID",
    "Vayne": "AD",
    "Veigar": "AP",
    "Velkoz": "AP",
    "Vex": "AP",
    "Vi": "AD",
    "Viego": "AD",
    "Viktor": "AP",
    "Vladimir": "AP",
    "Volibear": "HYBRID",
    # W
    "Warwick": "HYBRID",
    # X
    "Xayah": "AD",
    "Xerath": "AP",
    "XinZhao": "AD",
    # Y
    "Yasuo": "AD",
    "Yone": "AD",
    "Yorick": "AD",
    "Yuumi": "AP",
    # Z
    "Zac": "AP",
    "Zed": "AD",
    "Zeri": "AD",
    "Ziggs": "AP",
    "Zilean": "AP",
    "Zoe": "AP",
    "Zyra": "AP",
}

def get_champion_damage_type(champion_name):
    """
    Get the damage type for a champion.
    
    Args:
        champion_name (str): The name of the champion
        
    Returns:
        str: The damage type (AP, AD, or HYBRID)
    """
    # Remove spaces and special characters for matching
    clean_name = ''.join(c for c in champion_name if c.isalnum())
    
    # Try to find an exact match
    if clean_name in CHAMPION_DAMAGE_TYPES:
        return CHAMPION_DAMAGE_TYPES[clean_name]
    
    # Try case-insensitive match
    for champ_name, damage_type in CHAMPION_DAMAGE_TYPES.items():
        if clean_name.lower() == champ_name.lower():
            return damage_type
    
    # Default to AD if not found
    return "AD"


def calculate_team_damage_composition(team_participants):
    """
    Calculate the damage composition percentages for a team.
    
    Args:
        team_participants (list): List of participant objects
        
    Returns:
        dict: Dictionary with damage type percentages and counts
    """
    damage_counts = {"AP": 0, "AD": 0, "HYBRID": 0}
    
    for participant in team_participants:
        damage_type = get_champion_damage_type(participant.champion.name)
        damage_counts[damage_type] += 1
    
    total_champions = len(team_participants)
    damage_percentages = {
        "AP": round((damage_counts["AP"] / total_champions) * 100) if total_champions > 0 else 0,
        "AD": round((damage_counts["AD"] / total_champions) * 100) if total_champions > 0 else 0,
        "HYBRID": round((damage_counts["HYBRID"] / total_champions) * 100) if total_champions > 0 else 0,
    }
    
    return {
        "percentages": damage_percentages,
        "counts": damage_counts,
        "total": total_champions
    }


def analyze_team_synergy(team_composition):
    """
    Analyze team synergy based on damage composition.
    
    Args:
        team_composition (dict): Team damage composition from calculate_team_damage_composition
        
    Returns:
        dict: Dictionary with synergy analysis
    """
    percentages = team_composition["percentages"]
    counts = team_composition["counts"]
    
    # Determine if the team is balanced or skewed towards one damage type
    max_damage_type = max(percentages.items(), key=lambda x: x[1])
    
    synergy = {
        "balance": "Balanced" if max_damage_type[1] <= 60 else "Skewed",
        "primary_damage": max_damage_type[0],
        "primary_percentage": max_damage_type[1],
        "assessment": ""
    }
    
    # Provide a synergy assessment based on the damage composition
    if synergy["balance"] == "Balanced":
        synergy["assessment"] = "Good mix of damage types, difficult to counter-build."
    else:
        if max_damage_type[0] == "AP":
            synergy["assessment"] = "Heavy magic damage, vulnerable to MR stacking."
        elif max_damage_type[0] == "AD":
            synergy["assessment"] = "Heavy physical damage, vulnerable to armor stacking."
        else:
            synergy["assessment"] = "Significant hybrid damage, harder to counter-build."
    
    return synergy