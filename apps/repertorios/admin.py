from django.contrib import admin

from apps.repertorios.models import Repertorio, RepertorioMusica


class RepertorioMusicaInline(admin.TabularInline):
    model = RepertorioMusica
    extra = 1
    autocomplete_fields = ['musica', 'categoria_no_repertorio']
    ordering = ['ordem']


@admin.register(Repertorio)
class RepertorioAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'data_celebracao',
        'tipo_celebracao',
        'total_musicas',
        'created_at',
    ]
    list_filter = ['tipo_celebracao', 'data_celebracao']
    search_fields = ['nome', 'observacoes']
    date_hierarchy = 'data_celebracao'
    inlines = [RepertorioMusicaInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RepertorioMusica)
class RepertorioMusicaAdmin(admin.ModelAdmin):
    list_display = ['repertorio', 'musica', 'ordem', 'tom_no_repertorio']
    list_filter = ['repertorio', 'categoria_no_repertorio']
    search_fields = ['musica__titulo', 'repertorio__nome']
    autocomplete_fields = ['musica', 'repertorio', 'categoria_no_repertorio']
