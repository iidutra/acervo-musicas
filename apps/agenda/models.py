from django.db import models
from apps.core.choices import TIPO_CELEBRACAO_CHOICES
from .choices import TEMPO_LITURGICO_CHOICES


class TempoLiturgico(models.Model):
    """Período do ano litúrgico."""
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=TEMPO_LITURGICO_CHOICES, unique=True)
    cor_liturgica = models.CharField(
        max_length=30, blank=True,
        help_text='Ex: verde, roxo, branco, vermelho'
    )
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tempo Litúrgico'
        verbose_name_plural = 'Tempos Litúrgicos'

    def __str__(self):
        return self.nome


class Celebracao(models.Model):
    """Uma celebração agendada no calendário."""
    titulo = models.CharField(max_length=255)
    data = models.DateField()
    horario = models.TimeField(null=True, blank=True)
    tipo_celebracao = models.CharField(
        max_length=30, choices=TIPO_CELEBRACAO_CHOICES, default='missa_dominical'
    )
    tempo_liturgico = models.ForeignKey(
        TempoLiturgico,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='celebracoes',
    )
    local = models.CharField(max_length=255, blank=True)
    celebrante = models.CharField(max_length=255, blank=True)
    repertorio = models.ForeignKey(
        'repertorios.Repertorio',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='celebracoes',
        help_text='Repertório vinculado a esta celebração'
    )
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['data', 'horario']
        verbose_name = 'Celebração'
        verbose_name_plural = 'Celebrações'

    def __str__(self):
        return f'{self.titulo} - {self.data.strftime("%d/%m/%Y")}'

    @property
    def tem_repertorio(self):
        return self.repertorio is not None

    @property
    def data_passada(self):
        from django.utils import timezone
        return self.data < timezone.now().date()
