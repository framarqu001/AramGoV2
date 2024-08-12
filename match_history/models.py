from django.db import models
import datetime
import pytz


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
    puid = models.CharField(max_length=100, primary_key=True)
    gameName = models.CharField(max_length=50)
    tagLine = models.CharField(max_length=10)
    summoner_level = models.IntegerField()
    profile_icon = models.ForeignKey(ProfileIcon, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.gameName}: {self.tagLine}"


class Match(models.Model):
    match_id = models.CharField(primary_key=True, max_length=30)
    game_creation = models.DateTimeField()
    game_duration = models.IntegerField()
    game_mode = models.CharField(max_length=50)
    game_version = models.CharField(max_length=50)

    def get_participants(self):
        return self.participants.all()

    def __str__(self):
        return self.match_id


class Participant(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='participants')
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    champion = models.ForeignKey(Champion, on_delete=models.SET_NULL, null=True, related_name='participants')