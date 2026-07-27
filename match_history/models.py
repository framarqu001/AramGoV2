import pytz
import json
from django.db import models
from django.utils import timezone
from django.db import connection
from django.urls import reverse
from django import template
from django.core.cache import cache


class Champion(models.Model):
    champion_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    image_path = models.CharField(max_length=100)
    splash_image_path = models.CharField(max_length=100)

    def get_url(self):
        patch = cache.get("PATCH")
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{self.image_path}"

    def get_splash_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{self.splash_image_path}"

    def __str__(self):
        return self.name


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
    expanded_match_data = models.JSONField(null=True, blank=True)

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
            
    def get_expanded_match_data(self):
        """
        Get or generate expanded match data for detailed view.
        Returns cached data if available, otherwise computes and caches it.
        """
        if self.expanded_match_data:
            return self.expanded_match_data
            
        # Get all participants with related data
        participants = self.get_participants()
        
        # Calculate team statistics
        blue_team_stats = {
            'total_kills': 0,
            'total_deaths': 0,
            'total_assists': 0,
            'total_cs': 0,
        }
        
        red_team_stats = {
            'total_kills': 0,
            'total_deaths': 0,
            'total_assists': 0,
            'total_cs': 0,
        }
        
        blue_team_participants = []
        red_team_participants = []
        
        for participant in participants:
            participant_data = {
                'id': participant.id,
                'summoner_name': participant.game_name,
                'champion_name': participant.champion.name,
                'champion_image': participant.champion.get_url(),
                'kills': participant.kills,
                'deaths': participant.deaths,
                'assists': participant.assists,
                'creep_score': participant.creep_score,
                'kda': f"{((participant.kills + participant.assists) / participant.deaths if participant.deaths else participant.kills + participant.assists):.2f}",
                'items': [
                    getattr(participant.item1, 'get_url', lambda: None)() if participant.item1 else None,
                    getattr(participant.item2, 'get_url', lambda: None)() if participant.item2 else None,
                    getattr(participant.item3, 'get_url', lambda: None)() if participant.item3 else None,
                    getattr(participant.item4, 'get_url', lambda: None)() if participant.item4 else None,
                    getattr(participant.item5, 'get_url', lambda: None)() if participant.item5 else None,
                    getattr(participant.item6, 'get_url', lambda: None)() if participant.item6 else None,
                ],
                'spells': [
                    participant.spell1.get_url(),
                    participant.spell2.get_url(),
                ],
                'runes': [
                    getattr(participant.rune1, 'get_url', lambda: None)() if participant.rune1 else None,
                    getattr(participant.rune2, 'get_url', lambda: None)() if participant.rune2 else None,
                ],
                'win': participant.win,
            }
            
            if participant.team == self.BLUE_TEAM:
                blue_team_stats['total_kills'] += participant.kills
                blue_team_stats['total_deaths'] += participant.deaths
                blue_team_stats['total_assists'] += participant.assists
                blue_team_stats['total_cs'] += participant.creep_score
                blue_team_participants.append(participant_data)
            else:
                red_team_stats['total_kills'] += participant.kills
                red_team_stats['total_deaths'] += participant.deaths
                red_team_stats['total_assists'] += participant.assists
                red_team_stats['total_cs'] += participant.creep_score
                red_team_participants.append(participant_data)
        
        # Create expanded match data
        expanded_data = {
            'match_id': self.match_id,
            'game_duration': self.get_duration(),
            'game_minutes': self.get_minutes(),
            'game_mode': self.game_mode,
            'game_version': self.game_version,
            'patch': self.get_patch(),
            'winner': self.winner,
            'blue_team': {
                'stats': blue_team_stats,
                'participants': blue_team_participants,
                'win': self.winner == self.BLUE_TEAM,
            },
            'red_team': {
                'stats': red_team_stats,
                'participants': red_team_participants,
                'win': self.winner == self.RED_TEAM,
            },
        }
        
        # Cache the expanded data
        self.expanded_match_data = expanded_data
        self.save(update_fields=['expanded_match_data'])
        
        return expanded_data

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