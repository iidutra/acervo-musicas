from django.contrib import admin
from apps.importacao_exportacao.models import ImportacaoLote


@admin.register(ImportacaoLote)
class ImportacaoLoteAdmin(admin.ModelAdmin):
    list_display = (
        'nome_arquivo',
        'tipo_importacao',
        'status',
        'total_registros',
        'total_sucesso',
        'total_erro',
        'created_at',
    )
    list_filter = ('status', 'tipo_importacao')
    readonly_fields = (
        'nome_arquivo',
        'tipo_importacao',
        'arquivo',
        'status',
        'total_registros',
        'total_sucesso',
        'total_erro',
        'log',
        'created_at',
    )
    search_fields = ('nome_arquivo',)
    ordering = ('-created_at',)
