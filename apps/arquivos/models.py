import os
from django.db import models
from apps.core.choices import (
    TIPO_AUDIO_CHOICES, PROVIDER_CHOICES,
    TIPO_CONTEUDO_LINK_CHOICES, TIPO_CIFRA_CHOICES, TOM_CHOICES
)


def pdf_upload_path(instance, filename):
    return f'pdfs/musica_{instance.musica_id}/{filename}'


def audio_upload_path(instance, filename):
    return f'audios/musica_{instance.musica_id}/{filename}'


def cifra_upload_path(instance, filename):
    return f'cifras/musica_{instance.musica_id}/{filename}'


class PDFArquivo(models.Model):
    """PDF proprio vinculado a uma musica."""
    musica = models.ForeignKey(
        'musicas.Musica', on_delete=models.CASCADE, related_name='pdfs'
    )
    nome = models.CharField(max_length=255, help_text='Nome descritivo do arquivo')
    arquivo = models.FileField(upload_to=pdf_upload_path)
    tamanho_bytes = models.PositiveIntegerField(editable=False, default=0)
    pagina_inicial = models.PositiveIntegerField(null=True, blank=True)
    pagina_final = models.PositiveIntegerField(null=True, blank=True)
    texto_extraido = models.TextField(
        blank=True,
        help_text='Texto extraido automaticamente do PDF (pode conter erros)'
    )
    origem = models.CharField(max_length=50, blank=True, default='upload')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PDF'
        verbose_name_plural = 'PDFs'

    def __str__(self):
        return f'{self.nome} - {self.musica.titulo}'

    def save(self, *args, **kwargs):
        if self.arquivo:
            self.tamanho_bytes = self.arquivo.size
        super().save(*args, **kwargs)

    @property
    def nome_arquivo(self):
        return os.path.basename(self.arquivo.name) if self.arquivo else ''

    @property
    def tamanho_formatado(self):
        if self.tamanho_bytes < 1024:
            return f'{self.tamanho_bytes} B'
        elif self.tamanho_bytes < 1024 * 1024:
            return f'{self.tamanho_bytes / 1024:.1f} KB'
        return f'{self.tamanho_bytes / (1024 * 1024):.1f} MB'


class AudioProprio(models.Model):
    """Gravacao propria vinculada a uma musica."""
    musica = models.ForeignKey(
        'musicas.Musica', on_delete=models.CASCADE, related_name='audios'
    )
    nome = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to=audio_upload_path)
    tipo = models.CharField(max_length=20, choices=TIPO_AUDIO_CHOICES, default='ensaio')
    duracao_segundos = models.PositiveIntegerField(null=True, blank=True)
    formato = models.CharField(max_length=20, blank=True)
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audio Proprio'
        verbose_name_plural = 'Audios Proprios'

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()}) - {self.musica.titulo}'

    def save(self, *args, **kwargs):
        if self.arquivo and not self.formato:
            ext = os.path.splitext(self.arquivo.name)[1].lower().strip('.')
            self.formato = ext
        super().save(*args, **kwargs)

    @property
    def duracao_formatada(self):
        if not self.duracao_segundos:
            return ''
        mins = self.duracao_segundos // 60
        secs = self.duracao_segundos % 60
        return f'{mins}:{secs:02d}'


class LinkExterno(models.Model):
    """Link externo de referencia vinculado a uma musica."""
    musica = models.ForeignKey(
        'musicas.Musica', on_delete=models.CASCADE, related_name='links_externos'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='generico')
    tipo_conteudo = models.CharField(
        max_length=20, choices=TIPO_CONTEUDO_LINK_CHOICES, default='referencia'
    )
    titulo_externo = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=500)
    embed_url = models.URLField(max_length=500, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Link Externo'
        verbose_name_plural = 'Links Externos'

    def __str__(self):
        return f'{self.get_provider_display()}: {self.titulo_externo or self.url}'


class Cifra(models.Model):
    """Cifra vinculada a uma musica."""
    musica = models.ForeignKey(
        'musicas.Musica', on_delete=models.CASCADE, related_name='cifras'
    )
    tipo_cifra = models.CharField(max_length=10, choices=TIPO_CIFRA_CHOICES, default='texto')
    conteudo_texto = models.TextField(
        blank=True, help_text='Conteudo da cifra em texto'
    )
    arquivo_pdf = models.FileField(upload_to=cifra_upload_path, blank=True, null=True)
    link_referencia = models.URLField(max_length=500, blank=True)
    tom = models.CharField(max_length=10, choices=TOM_CHOICES, blank=True, default='')
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cifra'
        verbose_name_plural = 'Cifras'

    def __str__(self):
        return f'Cifra ({self.get_tipo_cifra_display()}) - {self.musica.titulo}'
