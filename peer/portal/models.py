from django.db import models
from django.utils.translation import ugettext_lazy as _


class TextChunkModel(models.Model):
    identifier = models.CharField(_(u'Identifier'), max_length=100, unique=True)
    text = models.TextField(_(u'Text'))
