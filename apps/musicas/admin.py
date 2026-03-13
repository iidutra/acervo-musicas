from django.contrib import admin
from .models import CategoriaLiturgica, Tag, Musica


@admin.register(CategoriaLiturgica)
class CategoriaLiturgicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativo', 'created_at')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    list_editable = ('ordem', 'ativo')
    ordering = ('ordem', 'nome')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'created_at')
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Musica)
class MusicaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tom_principal', 'ativo', 'created_at')
    list_filter = ('ativo', 'tom_principal', 'categorias')
    search_fields = ('titulo', 'subtitulo', 'letra')
    filter_horizontal = ('categorias', 'tags')
    readonly_fields = ('tom_normalizado', 'created_at', 'updated_at')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'subtitulo', 'letra'),
        }),
        ('Detalhes Musicais', {
            'fields': ('tom_principal', 'tom_normalizado', 'andamento', 'compasso'),
        }),
        ('Classificação', {
            'fields': ('categorias', 'tags'),
        }),
        ('Configurações', {
            'fields': ('origem', 'ativo', 'observacoes'),
        }),
        ('Datas', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
