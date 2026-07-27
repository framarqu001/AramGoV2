from django.db import migrations

# Champion role and damage type data
CHAMPION_DATA = {
    # Tanks
    'Amumu': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Braum': {'primary_role': 'tank', 'damage_type': 'physical'},
    'Cho\'Gath': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Dr. Mundo': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Leona': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Malphite': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Maokai': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Nautilus': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Ornn': {'primary_role': 'tank', 'damage_type': 'mixed'},
    'Rammus': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Sejuani': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Shen': {'primary_role': 'tank', 'damage_type': 'physical'},
    'Sion': {'primary_role': 'tank', 'damage_type': 'physical'},
    'Tahm Kench': {'primary_role': 'tank', 'damage_type': 'magical'},
    'Zac': {'primary_role': 'tank', 'damage_type': 'magical'},
    
    # Fighters
    'Aatrox': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Darius': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Garen': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Illaoi': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Irelia': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Jax': {'primary_role': 'fighter', 'damage_type': 'mixed'},
    'Lee Sin': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Mordekaiser': {'primary_role': 'fighter', 'damage_type': 'magical'},
    'Nasus': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Olaf': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Renekton': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Riven': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Sett': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Trundle': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Udyr': {'primary_role': 'fighter', 'damage_type': 'mixed'},
    'Vi': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Volibear': {'primary_role': 'fighter', 'damage_type': 'mixed'},
    'Warwick': {'primary_role': 'fighter', 'damage_type': 'mixed'},
    'Wukong': {'primary_role': 'fighter', 'damage_type': 'physical'},
    'Xin Zhao': {'primary_role': 'fighter', 'damage_type': 'physical'},
    
    # Mages
    'Ahri': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Anivia': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Annie': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Aurelion Sol': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Azir': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Brand': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Cassiopeia': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Fiddlesticks': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Heimerdinger': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Karma': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Karthus': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Lissandra': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Lux': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Malzahar': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Orianna': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Ryze': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Syndra': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Twisted Fate': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Veigar': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Viktor': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Vladimir': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Xerath': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Ziggs': {'primary_role': 'mage', 'damage_type': 'magical'},
    'Zyra': {'primary_role': 'mage', 'damage_type': 'magical'},
}

def populate_champion_data(apps, schema_editor):
    Champion = apps.get_model('match_history', 'Champion')
    
    for champion in Champion.objects.all():
        # Default values if champion not in our data
        data = CHAMPION_DATA.get(champion.name, {'primary_role': 'fighter', 'damage_type': 'physical'})
        
        champion.primary_role = data['primary_role']
        champion.damage_type = data['damage_type']
        champion.save()


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_add_team_composition'),
    ]

    operations = [
        migrations.RunPython(populate_champion_data),
    ]