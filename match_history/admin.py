from django.contrib import admin
from .models import UserProfile, Summoner, Champion, Match, Participant, AccountStats, SummonerChampionStats, ChampionStatsPatch

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_display_name', 'primary_summoner', 'profile_public', 'created_at')
    list_filter = ('profile_public', 'show_match_history', 'show_champion_stats', 'theme_preference', 'created_at')
    search_fields = ('user__username', 'user__email', 'display_name')
    filter_horizontal = ('connected_summoners',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'display_name', 'bio')
        }),
        ('Connected Accounts', {
            'fields': ('connected_summoners', 'primary_summoner')
        }),
        ('Privacy Settings', {
            'fields': ('profile_public', 'show_match_history', 'show_champion_stats')
        }),
        ('Display Preferences', {
            'fields': ('matches_per_page', 'theme_preference')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Display Name'

# Register other models if not already registered
admin.site.register(Summoner)
admin.site.register(Champion)
admin.site.register(Match)
admin.site.register(Participant)
admin.site.register(AccountStats)
admin.site.register(SummonerChampionStats)
admin.site.register(ChampionStatsPatch)
