from django.db import models
import datetime
from django.db import connection


class Champion(models.Model):
    champion_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    image_path = models.CharField(max_length=100)

    def get_full_url(self, patch):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{self.image_path}"

    def __str__(self):
        return self.name


class Item(models.Model):
    item_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    image_path = models.CharField(max_length=100)

    def get_full_url(self, patch):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/item/{self.image_path}"

    def __str__(self):
        return self.name


class ProfileIcon(models.Model):
    profile_id = models.CharField(primary_key=True, max_length=30)
    image_path = models.CharField(max_length=100)

    def get_full_url(self, patch):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/profileicon/{self.image_path}"

    def __str__(self):
        return self.profile_id


class Summoner(models.Model):
    puuid = models.CharField(max_length=100, primary_key=True)
    game_name = models.CharField(max_length=50, blank=True, default="")
    summoner_name = models.CharField(max_length=50, blank=True, default="")
    tag_line = models.CharField(max_length=10, blank=True, null=True)
    summoner_level = models.IntegerField()
    profile_icon = models.ForeignKey(ProfileIcon, on_delete=models.SET_NULL, null=True)

    # Get all matches in which a summoner was a participant in.
    def get_matches_queryset(self):
        # Returning a QuerySet instead of a list
        return Match.objects.filter(participants__summoner=self)

    def __str__(self):
        return f"{self.game_name}#{self.tag_line}"


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

    def get_minutes(self):
        SECONDS = 60
        return self.game_duration // SECONDS

    def get_participants(self):
        return self.participants.select_related("match").all()

    def __str__(self):
        return self.match_id


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
    creep_score = models.IntegerField()
    items = models.ManyToManyField(Item)
    team = models.IntegerField(choices=TEAM_CHOICES)
    win = models.BooleanField()

    def __str__(self):
        return f"{self.summoner} playing {self.champion} in match {self.match}"
