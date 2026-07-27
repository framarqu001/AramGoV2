from django.apps import AppConfig
from AramGoV2.util.current_patch import get_patch
from django.core.cache import cache


class MatchHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'match_history'

    def ready(self):
        patch = get_patch()
        if patch:
            # Updated cache timeout to 3 weeks (1814400 seconds)
            # to store patch version for 3 weeks as requested
            cache.set('PATCH', patch, timeout=1814400)
            print(f"{patch} cache successfully")
        else:
            print("Patch could not be retrieved")
