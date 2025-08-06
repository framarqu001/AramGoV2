from django.apps import AppConfig
from AramGoV2.util.current_patch import get_patch
from django.core.cache import cache


class MatchHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'match_history'

    def ready(self):
        patch = get_patch()
        if patch:
            # Updated cache timeout to 3 weeks (1814400 seconds) as requested
            # 3 weeks = 21 days * 24 hours * 60 minutes * 60 seconds = 1814400 seconds
            cache.set('PATCH', patch, timeout=1814400)
            print(f"{patch} cache successfully")
        else:
            print("Patch could not be retrieved")
