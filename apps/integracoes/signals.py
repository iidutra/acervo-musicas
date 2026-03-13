"""Signal para enriquecer automaticamente links externos ao criá-los."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.arquivos.models import LinkExterno
from apps.integracoes.services import enrich_link

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LinkExterno)
def auto_enrich_link(sender, instance, created, **kwargs):
    """Enriquece automaticamente um LinkExterno recém-criado."""
    if created and not instance.titulo_externo:
        try:
            enrich_link(instance)
        except Exception as e:
            logger.warning('Falha ao enriquecer link %s: %s', instance.pk, e)
