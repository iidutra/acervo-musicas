from django.db import models
from apps.core.choices import TIPO_IMPORTACAO_CHOICES, STATUS_IMPORTACAO_CHOICES


def importacao_upload_path(instance, filename):
    return f'importacoes/{filename}'


class ImportacaoLote(models.Model):
    """Registro de lote de importação."""
    tipo_importacao = models.CharField(max_length=10, choices=TIPO_IMPORTACAO_CHOICES)
    nome_arquivo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=importacao_upload_path)
    status = models.CharField(
        max_length=20, choices=STATUS_IMPORTACAO_CHOICES, default='pendente'
    )
    total_registros = models.PositiveIntegerField(default=0)
    total_sucesso = models.PositiveIntegerField(default=0)
    total_erro = models.PositiveIntegerField(default=0)
    log = models.TextField(blank=True, help_text='Log detalhado do processamento')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lote de Importação'
        verbose_name_plural = 'Lotes de Importação'

    def __str__(self):
        return f'{self.nome_arquivo} ({self.get_status_display()})'

    @property
    def total_processado(self):
        return self.total_sucesso + self.total_erro

    @property
    def percentual_sucesso(self):
        if self.total_registros == 0:
            return 0
        return round((self.total_sucesso / self.total_registros) * 100, 1)
