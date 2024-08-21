from django.db import models
from django.utils import timezone
from django.db import connection
from django.urls import reverse
from django import template

patch = "14.16.1"
class Champion(models.Model):
    champion_id = models.CharField(primary_key=True, max_length=30)
    name = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{self.image_path}"

    def __str__(self):
        return self.name


class Item(models.Model):
    item_id = models.CharField(max_length=30,primary_key=True)
    name = models.CharField(max_length=30)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/item/{self.image_path}"

    def __str__(self):
        return self.name


class ProfileIcon(models.Model):
    profile_id = models.CharField(primary_key=True, max_length=30)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/profileicon/{self.image_path}"

    def __str__(self):
        return self.profile_id

class SummonerSpell(models.Model):
    spell_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    image_path = models.CharField(max_length=100)

    def get_url(self):
        return f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/spell/{self.image_path}"

    def __str__(self):
        return f"{self.name} {self.spell_id}"
    
class Rune(models.Model):
    rune_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    image_path = models.CharField(max_length=50)
    
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
    profile_icon = models.ForeignKey(ProfileIcon, on_delete=models.SET_NULL,blank=True, null=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    # Get all matches in which a summoner was a participant in.
    def get_matches_queryset(self):
        # Returning a QuerySet instead of a list
        return Match.objects.filter(participants__summoner=self)


    def get_url(self):
        if self.game_name and self.tag_line:
            return reverse('match_history:details', args=[self.game_name, self.tag_line])
        return None
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

    def get_duration(self):
        minutes = self.game_duration // 60
        seconds = self.game_duration % 60
        return f"{minutes}:{seconds}"

    def get_minutes(self):
        return self.game_duration // 60
    def get_participants(self):
        return self.participants.select_related("match").all()

    def get_time_diff(self):
        now = timezone.now()
        difference = now - self.game_start
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
    rune1=models.ForeignKey(Rune, on_delete=models.CASCADE, related_name='participants_rune1')
    rune2=models.ForeignKey(Rune, on_delete=models.CASCADE, related_name='participants_rune2')
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
