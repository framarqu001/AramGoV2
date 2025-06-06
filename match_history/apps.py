from django.apps import AppConfig
from AramGoV2.util.current_patch import get_patch
from django.core.cache import cache


class MatchHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'match_history'

    def ready(self):
        patch = get_patch()
        if patch:
            # Increased cache timeout from 7 days (604800 seconds) to 30 days (2592000 seconds)
            # to ensure patch version is cached for longer as requested
            cache.set('PATCH', patch, timeout=2592000)
            print(f"{patch} cache successfully")
        else:
            print("Patch could not be retrieved")
