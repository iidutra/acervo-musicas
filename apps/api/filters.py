import django_filters

from apps.musicas.models import Musica


class MusicaFilter(django_filters.FilterSet):
    titulo = django_filters.CharFilter(lookup_expr='icontains')
    tom_principal = django_filters.CharFilter()
    categoria = django_filters.NumberFilter(field_name='categorias__id')
    tag = django_filters.NumberFilter(field_name='tags__id')
    ativo = django_filters.BooleanFilter()
    tem_pdf = django_filters.BooleanFilter(method='filter_tem_pdf')
    tem_audio = django_filters.BooleanFilter(method='filter_tem_audio')
    tem_cifra = django_filters.BooleanFilter(method='filter_tem_cifra')
    busca = django_filters.CharFilter(method='filter_busca')

    class Meta:
        model = Musica
        fields = ['titulo', 'tom_principal', 'ativo']

    def filter_tem_pdf(self, queryset, name, value):
        if value:
            return queryset.filter(pdfs__isnull=False).distinct()
        return queryset.filter(pdfs__isnull=True)

    def filter_tem_audio(self, queryset, name, value):
        if value:
            return queryset.filter(audios__isnull=False).distinct()
        return queryset.filter(audios__isnull=True)

    def filter_tem_cifra(self, queryset, name, value):
        if value:
            return queryset.filter(cifras__isnull=False).distinct()
        return queryset.filter(cifras__isnull=True)

    def filter_busca(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(titulo__icontains=value) |
            Q(subtitulo__icontains=value) |
            Q(letra__icontains=value)
        ).distinct()
