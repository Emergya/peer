from django.conf import settings


def get_settings(request):
    return {
        'MODERATION_ENABLED': settings.MODERATION_ENABLED
    }