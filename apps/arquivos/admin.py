from django.contrib import admin

from .models import PDFArquivo, AudioProprio, LinkExterno, Cifra


@admin.register(PDFArquivo)
class PDFArquivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'musica', 'tamanho_formatado', 'origem', 'created_at')
    list_filter = ('origem', 'created_at')
    search_fields = ('nome', 'musica__titulo', 'texto_extraido')
    readonly_fields = ('tamanho_bytes', 'tamanho_formatado', 'nome_arquivo', 'created_at')
    raw_id_fields = ('musica',)


@admin.register(AudioProprio)
class AudioProprioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'musica', 'tipo', 'formato', 'duracao_formatada', 'created_at')
    list_filter = ('tipo', 'formato', 'created_at')
    search_fields = ('nome', 'musica__titulo', 'observacoes')
    readonly_fields = ('created_at',)
    raw_id_fields = ('musica',)


@admin.register(LinkExterno)
class LinkExternoAdmin(admin.ModelAdmin):
    list_display = ('titulo_externo', 'musica', 'provider', 'tipo_conteudo', 'url', 'created_at')
    list_filter = ('provider', 'tipo_conteudo', 'created_at')
    search_fields = ('titulo_externo', 'musica__titulo', 'url', 'observacoes')
    readonly_fields = ('created_at',)
    raw_id_fields = ('musica',)


@admin.register(Cifra)
class CifraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'musica', 'tipo_cifra', 'tom', 'created_at')
    list_filter = ('tipo_cifra', 'tom', 'created_at')
    search_fields = ('musica__titulo', 'conteudo_texto', 'observacoes')
    readonly_fields = ('created_at',)
    raw_id_fields = ('musica',)
