from django.contrib import admin
from .models import Match, Participant, Champion, Item, ProfileIcon, SummonerSpell, Rune, Summoner, TimelineEvent

# Register your models here.
admin.site.register(Match)
admin.site.register(Participant)
admin.site.register(Champion)
admin.site.register(Item)
admin.site.register(ProfileIcon)
admin.site.register(SummonerSpell)
admin.site.register(Rune)
admin.site.register(Summoner)
admin.site.register(TimelineEvent)
