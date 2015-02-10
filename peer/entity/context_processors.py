from django.conf import settings


def global_settings(request):
    return {
        'MODERATION_ENABLED': settings.MODERATION_ENABLED
    }