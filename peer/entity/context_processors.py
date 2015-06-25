from django.conf import settings


def get_settings(request):
    return {
        'MODERATION_ENABLED': getattr(settings, 'MODERATION_ENABLED', False)
    }