from django.contrib import admin
from .models import (
    Champion, Item, ProfileIcon, SummonerSpell, Rune, 
    Summoner, Match, Participant, SummonerChampionStats, 
    AccountStats, ChampionStatsPatch
)

# Register your models here.
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'champion', 'match', 'kills', 'deaths', 'assists', 
                   'total_damage_dealt', 'damage_to_champions', 'vision_score', 
                   'gold_earned', 'largest_killing_spree')
    search_fields = ('game_name', 'champion__name')
    list_filter = ('win', 'team')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'game_mode', 'game_start', 'game_duration', 'winner')
    search_fields = ('match_id',)
    list_filter = ('game_mode', 'winner')

@admin.register(Summoner)
class SummonerAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'tag_line', 'summoner_level')
    search_fields = ('game_name', 'tag_line')

admin.site.register(Champion)
admin.site.register(Item)
admin.site.register(ProfileIcon)
admin.site.register(SummonerSpell)
admin.site.register(Rune)
admin.site.register(SummonerChampionStats)
admin.site.register(AccountStats)
admin.site.register(ChampionStatsPatch)
