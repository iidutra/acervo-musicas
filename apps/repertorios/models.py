from django.db import models
from apps.core.choices import TIPO_CELEBRACAO_CHOICES, TOM_CHOICES


class Repertorio(models.Model):
    """Repertório musical para uma celebração."""
    nome = models.CharField(max_length=255)
    data_celebracao = models.DateField(null=True, blank=True)
    tipo_celebracao = models.CharField(
        max_length=30, choices=TIPO_CELEBRACAO_CHOICES, default='missa_dominical'
    )
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_celebracao', '-created_at']
        verbose_name = 'Repertório'
        verbose_name_plural = 'Repertórios'

    def __str__(self):
        data = self.data_celebracao.strftime('%d/%m/%Y') if self.data_celebracao else 'Sem data'
        return f'{self.nome} ({data})'

    @property
    def total_musicas(self):
        return self.itens.count()


class RepertorioMusica(models.Model):
    """Associação entre repertório e música com dados específicos."""
    repertorio = models.ForeignKey(
        Repertorio, on_delete=models.CASCADE, related_name='itens'
    )
    musica = models.ForeignKey(
        'musicas.Musica', on_delete=models.CASCADE, related_name='repertorios'
    )
    ordem = models.PositiveIntegerField(default=0)
    categoria_no_repertorio = models.ForeignKey(
        'musicas.CategoriaLiturgica',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Categoria/momento litúrgico neste repertório'
    )
    tom_no_repertorio = models.CharField(
        max_length=10, choices=TOM_CHOICES, blank=True, default='',
        help_text='Tom específico para esta celebração (se diferente do principal)'
    )
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Música no Repertório'
        verbose_name_plural = 'Músicas no Repertório'
        unique_together = ['repertorio', 'musica', 'ordem']

    def __str__(self):
        return f'{self.ordem}. {self.musica.titulo}'

    @property
    def tom_efetivo(self):
        """Return repertoire-specific key or the song's main key."""
        return self.tom_no_repertorio or self.musica.tom_principal
