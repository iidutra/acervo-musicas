from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.musicas.models import Musica, CategoriaLiturgica, Tag
from apps.arquivos.models import PDFArquivo, AudioProprio, LinkExterno, Cifra
from apps.repertorios.models import Repertorio, RepertorioMusica
from apps.agenda.models import Celebracao, TempoLiturgico

from .serializers import (
    MusicaListSerializer, MusicaDetailSerializer, MusicaWriteSerializer,
    CategoriaLiturgicaSerializer, TagSerializer,
    PDFArquivoSerializer, AudioProprioSerializer,
    LinkExternoSerializer, CifraSerializer,
    RepertorioListSerializer, RepertorioDetailSerializer,
    RepertorioMusicaSerializer,
    CelebracaoSerializer, TempoLiturgicoSerializer,
)
from .filters import MusicaFilter


class CategoriaLiturgicaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaLiturgica.objects.all()
    serializer_class = CategoriaLiturgicaSerializer
    search_fields = ['nome']
    ordering_fields = ['nome', 'ordem']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['nome']


class MusicaViewSet(viewsets.ModelViewSet):
    queryset = Musica.objects.prefetch_related(
        'categorias', 'tags', 'pdfs', 'audios', 'links_externos', 'cifras'
    )
    filterset_class = MusicaFilter
    search_fields = ['titulo', 'subtitulo', 'letra']
    ordering_fields = ['titulo', 'tom_principal', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MusicaListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return MusicaWriteSerializer
        return MusicaDetailSerializer

    @action(detail=True, methods=['post'])
    def toggle_ativo(self, request, pk=None):
        musica = self.get_object()
        musica.ativo = not musica.ativo
        musica.save(update_fields=['ativo', 'updated_at'])
        return Response({
            'id': musica.pk,
            'ativo': musica.ativo,
            'message': f'Música {"ativada" if musica.ativo else "desativada"}.',
        })

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas gerais do acervo."""
        return Response({
            'total_musicas': Musica.objects.filter(ativo=True).count(),
            'total_pdfs': PDFArquivo.objects.count(),
            'total_audios': AudioProprio.objects.count(),
            'total_links': LinkExterno.objects.count(),
            'total_cifras': Cifra.objects.count(),
            'total_categorias': CategoriaLiturgica.objects.filter(ativo=True).count(),
            'total_tags': Tag.objects.count(),
        })


class PDFArquivoViewSet(viewsets.ModelViewSet):
    queryset = PDFArquivo.objects.select_related('musica')
    serializer_class = PDFArquivoSerializer
    filterset_fields = ['musica']


class AudioProprioViewSet(viewsets.ModelViewSet):
    queryset = AudioProprio.objects.select_related('musica')
    serializer_class = AudioProprioSerializer
    filterset_fields = ['musica', 'tipo']


class LinkExternoViewSet(viewsets.ModelViewSet):
    queryset = LinkExterno.objects.select_related('musica')
    serializer_class = LinkExternoSerializer
    filterset_fields = ['musica', 'provider', 'tipo_conteudo']


class CifraViewSet(viewsets.ModelViewSet):
    queryset = Cifra.objects.select_related('musica')
    serializer_class = CifraSerializer
    filterset_fields = ['musica', 'tipo_cifra']


class RepertorioViewSet(viewsets.ModelViewSet):
    queryset = Repertorio.objects.prefetch_related('itens__musica')
    search_fields = ['nome']
    filterset_fields = ['tipo_celebracao']
    ordering_fields = ['nome', 'data_celebracao', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return RepertorioListSerializer
        return RepertorioDetailSerializer

    @action(detail=True, methods=['get'])
    def recomendacoes(self, request, pk=None):
        """Retorna recomendações de músicas para este repertório."""
        from apps.repertorios.services import RecomendacaoService
        repertorio = self.get_object()
        service = RecomendacaoService()
        recs = service.recomendar_repertorio_completo(
            tipo_celebracao=repertorio.tipo_celebracao,
        )
        result = {}
        for momento, sugestoes in recs.items():
            result[momento] = [
                {
                    'musica_id': s['musica'].pk,
                    'titulo': s['musica'].titulo,
                    'tom': s['musica'].tom_principal,
                    'score': s['score'],
                    'razoes': s['razoes'],
                }
                for s in sugestoes
            ]
        return Response(result)


class RepertorioMusicaViewSet(viewsets.ModelViewSet):
    queryset = RepertorioMusica.objects.select_related('musica', 'repertorio')
    serializer_class = RepertorioMusicaSerializer
    filterset_fields = ['repertorio', 'musica']


class TempoLiturgicoViewSet(viewsets.ModelViewSet):
    queryset = TempoLiturgico.objects.all()
    serializer_class = TempoLiturgicoSerializer
    search_fields = ['nome']


class CelebracaoViewSet(viewsets.ModelViewSet):
    queryset = Celebracao.objects.select_related('tempo_liturgico', 'repertorio')
    serializer_class = CelebracaoSerializer
    filterset_fields = ['tipo_celebracao', 'tempo_liturgico', 'data']
    search_fields = ['titulo', 'local', 'celebrante']
    ordering_fields = ['data', 'horario']
