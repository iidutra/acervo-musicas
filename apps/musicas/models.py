from django.db import models
from apps.core.choices import TOM_CHOICES, ORIGEM_CHOICES


class CategoriaLiturgica(models.Model):
    """Categoria litúrgica para classificação de músicas."""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveIntegerField(default=0, help_text='Ordem de exibição')
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Categoria Litúrgica'
        verbose_name_plural = 'Categorias Litúrgicas'

    def __str__(self):
        return self.nome


class Tag(models.Model):
    """Tag livre para facilitar busca e agrupamento."""
    nome = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.nome


class Musica(models.Model):
    """Modelo principal do acervo - uma música."""
    titulo = models.CharField(max_length=255)
    subtitulo = models.CharField(max_length=255, blank=True)
    letra = models.TextField(blank=True, help_text='Letra completa da música')
    tom_principal = models.CharField(
        max_length=10,
        choices=TOM_CHOICES,
        default='NI',
        help_text='Tom principal da música'
    )
    tom_normalizado = models.CharField(
        max_length=10,
        blank=True,
        editable=False,
        help_text='Tom normalizado automaticamente'
    )
    andamento = models.CharField(max_length=50, blank=True, help_text='Ex: Moderado, Rápido, Lento')
    compasso = models.CharField(max_length=20, blank=True, help_text='Ex: 4/4, 3/4, 6/8')
    observacoes = models.TextField(blank=True)
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='manual')
    ativo = models.BooleanField(default=True)

    categorias = models.ManyToManyField(
        CategoriaLiturgica,
        blank=True,
        related_name='musicas'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='musicas'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Música'
        verbose_name_plural = 'Músicas'

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        # Auto-normalize tone
        from apps.core.utils import normalizar_tom
        if self.tom_principal and self.tom_principal != 'NI':
            normalized = normalizar_tom(self.tom_principal)
            self.tom_normalizado = normalized or ''
        else:
            self.tom_normalizado = ''
        super().save(*args, **kwargs)

    @property
    def tem_pdf(self):
        return self.pdfs.exists()

    @property
    def tem_audio(self):
        return self.audios.exists()

    @property
    def tem_cifra(self):
        return self.cifras.exists()

    @property
    def tem_link(self):
        return self.links_externos.exists()
