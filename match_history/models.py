import pytz
from django.db import models
from django.utils import timezone
from django.db import connection
from django.urls import reverse
from django import template
from django.core.cache import cache
from collections import Counter


class Champion(models.Model):
    # Champion role constants
    TANK = 'tank'
    FIGHTER = 'fighter'
    MAGE = 'mage'
    ASSASSIN = 'assassin'
    MARKSMAN = 'marksman'
    SUPPORT = 'support'
    
    ROLE_CHOICES = [
        (TANK, 'Tank'),
        (FIGHTER, 'Fighter'),
        (MAGE, 'Mage'),
        (ASSASSIN, 'Assassin'),
        (MARKSMAN, 'Marksman'),
        (SUPPORT, 'Support'),
    ]
    
    # Damage type constants
    PHYSICAL = 'physical'
    MAGICAL = 'magical'
    MIXED = 'mixed'
    
    DAMAGE_TYPE_CHOICES = [
        (PHYSICAL, 'Physical'),
        (MAGICAL, 'Magical'),
        (MIXED, 'Mixed'),
    ]
    
    champion_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    image_path = models.CharField(max_length=100)
    splash_image_path = models.CharField(max_length=100)
    primary_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=FIGHTER)
    secondary_role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    damage_type = models.CharField(max_length=20, choices=DAMAGE_TYPE_CHOICES, default=PHYSICAL)

    def get_url(self):
        patch = cache.get("PATCH")
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{self.image_path}"

    def get_splash_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{self.splash_image_path}"
        
    def get_role_display_name(self):
        return dict(self.ROLE_CHOICES).get(self.primary_role, self.primary_role)
        
    def get_damage_type_display_name(self):
        return dict(self.DAMAGE_TYPE_CHOICES).get(self.damage_type, self.damage_type)

    def __str__(self):
        return self.name


class TeamComposition(models.Model):
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='team_compositions')
    team = models.IntegerField(choices=[(100, 'Blue Team'), (200, 'Red Team')])
    
    # Cached composition data
    role_distribution = models.JSONField(default=dict)
    damage_distribution = models.JSONField(default=dict)
    synergy_score = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('match', 'team')
    
    def __str__(self):
        return f"Team Composition for {self.match} - Team {self.team}"
    
    @classmethod
    def calculate_for_match(cls, match):
        """Calculate team compositions for both teams in a match"""
        blue_team = []
        red_team = []
        
        for participant in match.participants.select_related('champion').all():
            if participant.team == 100:  # Blue team
                blue_team.append(participant)
            else:  # Red team
                red_team.append(participant)
        
        # Calculate and save compositions for both teams
        blue_comp = cls._calculate_composition(match, 100, blue_team)
        red_comp = cls._calculate_composition(match, 200, red_team)
        
        return blue_comp, red_comp
    
    @classmethod
    def _calculate_composition(cls, match, team_id, participants):
        """Calculate composition data for a team"""
        # Get or create team composition
        team_comp, created = cls.objects.get_or_create(
            match=match,
            team=team_id
        )
        
        # Calculate role distribution
        roles = []
        for participant in participants:
            roles.append(participant.champion.primary_role)
            if participant.champion.secondary_role:
                roles.append(participant.champion.secondary_role)
        
        role_counter = Counter(roles)
        total_roles = len(roles)
        role_distribution = {role: count / total_roles * 100 for role, count in role_counter.items()}
        
        # Calculate damage distribution
        damage_types = [p.champion.damage_type for p in participants]
        damage_counter = Counter(damage_types)
        total_champions = len(participants)
        damage_distribution = {dtype: count / total_champions * 100 for dtype, count in damage_counter.items()}
        
        # Calculate synergy score
        synergy_score = cls._calculate_synergy_score(role_counter, damage_counter)
        
        # Update team composition
        team_comp.role_distribution = role_distribution
        team_comp.damage_distribution = damage_distribution
        team_comp.synergy_score = synergy_score
        team_comp.save()
        
        return team_comp
    
    @staticmethod
    def _calculate_synergy_score(role_counter, damage_counter):
        """Calculate team synergy score based on role and damage distribution"""
        score = 0
        
        # Ideal team has at least one tank
        if role_counter.get(Champion.TANK, 0) >= 1:
            score += 20
        
        # Ideal team has at least one support
        if role_counter.get(Champion.SUPPORT, 0) >= 1:
            score += 20
        
        # Ideal team has at least one marksman or mage for consistent damage
        if role_counter.get(Champion.MARKSMAN, 0) >= 1 or role_counter.get(Champion.MAGE, 0) >= 1:
            score += 20
        
        # Balanced damage types (both physical and magical)
        if damage_counter.get(Champion.PHYSICAL, 0) >= 1 and damage_counter.get(Champion.MAGICAL, 0) >= 1:
            score += 20
        
        # Avoid too many of the same role
        if max(role_counter.values()) <= 2:
            score += 20
            
        return score
    
    def get_role_distribution_formatted(self):
        """Return role distribution as a formatted dictionary"""
        result = {}
        for role, percentage in self.role_distribution.items():
            role_name = dict(Champion.ROLE_CHOICES).get(role, role)
            result[role_name] = round(percentage)
        return result
    
    def get_damage_distribution_formatted(self):
        """Return damage distribution as a formatted dictionary"""
        result = {}
        for damage_type, percentage in self.damage_distribution.items():
            damage_name = dict(Champion.DAMAGE_TYPE_CHOICES).get(damage_type, damage_type)
            result[damage_name] = round(percentage)
        return result
    
    def get_synergy_description(self):
        """Return a description of the team synergy based on the score"""
        if self.synergy_score >= 80:
            return "Excellent team composition with great balance and synergy."
        elif self.synergy_score >= 60:
            return "Good team composition with decent balance."
        elif self.synergy_score >= 40:
            return "Average team composition with some imbalances."
        else:
            return "Suboptimal team composition with significant imbalances."


class Item(models.Model):
    item_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)

    def get_url(self):
        patch = cache.get("PATCH")
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/item/{self.image_path}"

    def __str__(self):
        return self.name


class ProfileIcon(models.Model):
    profile_id = models.CharField(primary_key=True, max_length=100)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        patch = cache.get("PATCH")
        print("here")
        print(patch)
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/profileicon/{self.image_path}"

    def __str__(self):
        return self.profile_id


class SummonerSpell(models.Model):
    spell_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        patch = cache.get("PATCH")
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/spell/{self.image_path}"

    def __str__(self):
        return f"{self.name} {self.spell_id}"


class Rune(models.Model):
    rune_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/img/{self.image_path}"


class Summoner(models.Model):
    puuid = models.CharField(max_length=100, primary_key=True)
    game_name = models.CharField(max_length=50, blank=True, default="")
    normalized_game_name = models.CharField(max_length=50, blank=True, default="")
    summoner_name = models.CharField(max_length=50, blank=True, default="")
    tag_line = models.CharField(max_length=10, blank=True, default="")
    normalized_tag_line = models.CharField(max_length=50, blank=True, default="")
    summoner_level = models.IntegerField(blank=True, null=True)
    profile_icon = models.ForeignKey(ProfileIcon, on_delete=models.SET_NULL, blank=True, null=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=100, blank=True, null=True)
    being_parsed = models.BooleanField(default=False)
    parsed_matches = models.IntegerField(default=False)
    total_matches = models.IntegerField(default=0)

    def get_matches_queryset(self):
        return Match.objects.filter(participants__summoner=self)

    def get_url(self):
        if self.game_name and self.tag_line:
            return reverse('match_history:details', args=[self.game_name, self.tag_line])
        return None

    def get_full_name(self):
        return f"{self.game_name}#{self.tag_line}"
    
    def __str__(self):
        return f"Summoner:{self.game_name} {self.puuid}"


class Match(models.Model):
    BLUE_TEAM = 100
    RED_TEAM = 200

    WINNER_CHOICES = [
        (BLUE_TEAM, 'Blue Win'),
        (RED_TEAM, 'Red Win'),
    ]

    match_id = models.CharField(primary_key=True, max_length=30)
    game_start = models.DateTimeField()
    game_duration = models.IntegerField()
    game_mode = models.CharField(max_length=50)
    game_version = models.CharField(max_length=50)
    winner = models.IntegerField(choices=WINNER_CHOICES)
    new_match = models.BooleanField(default=False)

    def get_patch(self):
        return '.'.join(self.game_version.split('.')[:2])

    def get_duration(self):
        minutes = self.game_duration // 60
        seconds = self.game_duration % 60
        return f"{minutes}:{seconds}"

    def get_minutes(self):
        return self.game_duration // 60

    def get_participants(self):
        return self.participants.select_related("match").all()
        
    def get_team_compositions(self):
        """Get or calculate team compositions for this match"""
        compositions = self.team_compositions.all()
        if compositions.count() < 2:
            # Calculate compositions if they don't exist
            compositions = TeamComposition.calculate_for_match(self)
        else:
            compositions = list(compositions)
            
        # Return as a dictionary with team IDs as keys
        return {comp.team: comp for comp in compositions}

    def get_time_diff(self):
        la_timezone = pytz.timezone('America/Los_Angeles')

        now = timezone.now().astimezone(la_timezone)
        game_start_la = self.game_start.astimezone(la_timezone)

        difference = now - game_start_la
        seconds = difference.total_seconds()
        minutes = seconds // 60
        hours = seconds // 3600
        days = seconds // 86400

        if minutes < 60:
            return f"{int(minutes)} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        elif days < 30:
            return f"{int(days)} days ago"
        else:
            return self.game_start.strftime('%m-%d-%Y')

    def __str__(self):
        return self.match_id

    class Meta:
        ordering = ['-game_start']


class Participant(models.Model):
    BLUE_TEAM = 100
    RED_TEAM = 200

    TEAM_CHOICES = [
        (BLUE_TEAM, 'Blue Team'),
        (RED_TEAM, 'Red Team'),
    ]
    # A match has many participants. Participants belong to one match.
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participants')
    # A Summoner can be a participant in multiple matches.
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name='participants')
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name='participants')
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    spell1 = models.ForeignKey(SummonerSpell, on_delete=models.CASCADE, related_name='participants_spell1')
    spell2 = models.ForeignKey(SummonerSpell, on_delete=models.CASCADE, related_name='participants_spell2')
    rune1 = models.ForeignKey(Rune, on_delete=models.CASCADE, related_name='participants_rune1', blank=True, null=True)
    rune2 = models.ForeignKey(Rune, on_delete=models.CASCADE, related_name='participants_rune2', blank=True, null=True)
    creep_score = models.IntegerField()
    item1 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item1")
    item2 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item2")
    item3 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item3")
    item4 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item4")
    item5 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item5")
    item6 = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True, related_name="participants_item6")
    team = models.IntegerField(choices=TEAM_CHOICES)
    win = models.BooleanField()
    game_name = models.CharField(max_length=50)

    def match_result(self):
        if self.win:
            return "Victory"
        return "Defeat"

    def __str__(self):
        return f"{self.game_name} playing {self.champion} in match {self.match}"


class SummonerChampionStats(models.Model):
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name='champion_stats')
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name='summoner_stats')
    total_played = models.IntegerField(default=0)
    duration_played = models.IntegerField(default=0)  # in seconds
    total_creep_score = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_kills = models.IntegerField(default=0)
    total_deaths = models.IntegerField(default=0)
    total_assists = models.IntegerField(default=0)
    year = models.IntegerField(default=2024)

    class Meta:
        unique_together = ('summoner', 'champion', 'year')

    def win_rate(self):
        return (self.total_wins / self.total_played) * 100 if self.total_played > 0 else 0

    def __str__(self):
        return f"stats for {self.summoner.game_name}:{self.champion.name} in {self.year}"

    def update_stats(self, participant: Participant, match: Match):
        self.total_played += 1
        self.duration_played += match.game_duration
        self.total_creep_score += participant.creep_score
        if participant.win:
            self.total_wins += 1
        else:
            self.total_losses += 1
        self.total_kills += participant.kills
        self.total_deaths += participant.deaths
        self.total_assists += participant.assists
        self.save()


class AccountStats(models.Model):
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE, related_name='account_stats')
    total_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    total_kills = models.IntegerField(default=0)
    total_deaths = models.IntegerField(default=0)
    total_assists = models.IntegerField(default=0)
    snowballs_thrown = models.IntegerField(default=0)
    snowball_hits = models.IntegerField(default=0)
    year = models.IntegerField(default=2024)

    class Meta:
        unique_together = ('summoner', 'year')

    def __str__(self):
        return f"Account stats for {self.summoner}"
    
    def get_snowball_percent(self):
        hit_rate = (self.snowball_hits / self.snowballs_thrown * 100) if self.snowballs_thrown > 0 else 0
        return  f"{int(round(hit_rate))}%"

    def update_stats(self, participant: Participant, snowballs):
        self.total_played += 1
        if participant.win:
            self.total_wins += 1
        else:
            self.total_losses += 1
        self.total_kills += participant.kills
        self.total_deaths += participant.deaths
        self.total_assists += participant.assists
        self.snowballs_thrown += snowballs[1]
        self.snowball_hits += snowballs[0]
        self.save()


class ChampionStatsPatch(models.Model):
    champion = models.ForeignKey(Champion, on_delete=models.CASCADE, related_name='stats')
    patch = models.CharField(max_length=10)
    total_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)

    class Meta:
        unique_together = ('champion', 'patch')

    def __str__(self):
        return f"Stats {self.champion}:{self.patch}"

    def update_stats(self, participant: Participant):
        self.total_played += 1
        if participant.win:
            self.total_wins += 1
        else:
            self.total_losses += 1
        self.save()