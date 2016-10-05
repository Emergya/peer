from django.conf import settings


def get_settings(request):
    return {
        'MODERATION_ENABLED': getattr(settings, 'MODERATION_ENABLED', False),
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    }
