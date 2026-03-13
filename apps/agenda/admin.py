from django.contrib import admin
from .models import Celebracao, TempoLiturgico


@admin.register(TempoLiturgico)
class TempoLiturgicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cor_liturgica']
    list_filter = ['tipo']
    search_fields = ['nome']


@admin.register(Celebracao)
class CelebracaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data', 'horario', 'tipo_celebracao', 'tempo_liturgico', 'tem_repertorio']
    list_filter = ['tipo_celebracao', 'tempo_liturgico', 'data']
    search_fields = ['titulo', 'local', 'celebrante']
    date_hierarchy = 'data'
    raw_id_fields = ['repertorio']

    def tem_repertorio(self, obj):
        return obj.tem_repertorio
    tem_repertorio.boolean = True
    tem_repertorio.short_description = 'Repertório?'
