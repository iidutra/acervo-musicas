from rest_framework import serializers

from apps.musicas.models import Musica, CategoriaLiturgica, Tag
from apps.arquivos.models import PDFArquivo, AudioProprio, LinkExterno, Cifra
from apps.repertorios.models import Repertorio, RepertorioMusica
from apps.agenda.models import Celebracao, TempoLiturgico


class CategoriaLiturgicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaLiturgica
        fields = ['id', 'nome', 'descricao', 'ordem', 'ativo', 'created_at']
        read_only_fields = ['created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nome', 'created_at']
        read_only_fields = ['created_at']


class PDFArquivoSerializer(serializers.ModelSerializer):
    nome_arquivo = serializers.ReadOnlyField()
    tamanho_formatado = serializers.ReadOnlyField()

    class Meta:
        model = PDFArquivo
        fields = [
            'id', 'musica', 'nome', 'arquivo', 'tamanho_bytes',
            'tamanho_formatado', 'nome_arquivo',
            'pagina_inicial', 'pagina_final', 'texto_extraido',
            'origem', 'created_at',
        ]
        read_only_fields = ['tamanho_bytes', 'texto_extraido', 'created_at']


class AudioProprioSerializer(serializers.ModelSerializer):
    duracao_formatada = serializers.ReadOnlyField()

    class Meta:
        model = AudioProprio
        fields = [
            'id', 'musica', 'nome', 'arquivo', 'tipo',
            'duracao_segundos', 'duracao_formatada', 'formato',
            'observacoes', 'created_at',
        ]
        read_only_fields = ['formato', 'created_at']


class LinkExternoSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    tipo_conteudo_display = serializers.CharField(source='get_tipo_conteudo_display', read_only=True)

    class Meta:
        model = LinkExterno
        fields = [
            'id', 'musica', 'provider', 'provider_display',
            'tipo_conteudo', 'tipo_conteudo_display',
            'titulo_externo', 'url', 'embed_url',
            'external_id', 'thumbnail_url',
            'observacoes', 'created_at',
        ]
        read_only_fields = ['created_at']


class CifraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cifra
        fields = [
            'id', 'musica', 'tipo_cifra', 'conteudo_texto',
            'arquivo_pdf', 'link_referencia', 'tom',
            'observacoes', 'created_at',
        ]
        read_only_fields = ['created_at']


class MusicaListSerializer(serializers.ModelSerializer):
    """Serializer compacto para listagens."""
    categorias = CategoriaLiturgicaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tem_pdf = serializers.BooleanField(read_only=True)
    tem_audio = serializers.BooleanField(read_only=True)
    tem_cifra = serializers.BooleanField(read_only=True)

    class Meta:
        model = Musica
        fields = [
            'id', 'titulo', 'subtitulo', 'tom_principal', 'tom_normalizado',
            'ativo', 'categorias', 'tags',
            'tem_pdf', 'tem_audio', 'tem_cifra',
            'created_at', 'updated_at',
        ]


class MusicaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo com relacionamentos."""
    categorias = CategoriaLiturgicaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    pdfs = PDFArquivoSerializer(many=True, read_only=True)
    audios = AudioProprioSerializer(many=True, read_only=True)
    links_externos = LinkExternoSerializer(many=True, read_only=True)
    cifras = CifraSerializer(many=True, read_only=True)
    categoria_ids = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaLiturgica.objects.all(),
        many=True, write_only=True, source='categorias', required=False,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, write_only=True, source='tags', required=False,
    )

    class Meta:
        model = Musica
        fields = [
            'id', 'titulo', 'subtitulo', 'letra',
            'tom_principal', 'tom_normalizado',
            'andamento', 'compasso', 'observacoes',
            'origem', 'ativo',
            'categorias', 'tags', 'categoria_ids', 'tag_ids',
            'pdfs', 'audios', 'links_externos', 'cifras',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['tom_normalizado', 'created_at', 'updated_at']


class MusicaWriteSerializer(serializers.ModelSerializer):
    """Serializer para criação/atualização de músicas."""
    categoria_ids = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaLiturgica.objects.all(),
        many=True, source='categorias', required=False,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, source='tags', required=False,
    )

    class Meta:
        model = Musica
        fields = [
            'titulo', 'subtitulo', 'letra',
            'tom_principal', 'andamento', 'compasso',
            'observacoes', 'origem', 'ativo',
            'categoria_ids', 'tag_ids',
        ]


class RepertorioMusicaSerializer(serializers.ModelSerializer):
    musica_titulo = serializers.CharField(source='musica.titulo', read_only=True)
    tom_efetivo = serializers.ReadOnlyField()

    class Meta:
        model = RepertorioMusica
        fields = [
            'id', 'repertorio', 'musica', 'musica_titulo',
            'ordem', 'categoria_no_repertorio', 'tom_no_repertorio',
            'tom_efetivo', 'observacoes',
        ]


class RepertorioListSerializer(serializers.ModelSerializer):
    total_musicas = serializers.ReadOnlyField()

    class Meta:
        model = Repertorio
        fields = [
            'id', 'nome', 'data_celebracao', 'tipo_celebracao',
            'total_musicas', 'observacoes', 'created_at', 'updated_at',
        ]


class RepertorioDetailSerializer(serializers.ModelSerializer):
    itens = RepertorioMusicaSerializer(many=True, read_only=True)
    total_musicas = serializers.ReadOnlyField()

    class Meta:
        model = Repertorio
        fields = [
            'id', 'nome', 'data_celebracao', 'tipo_celebracao',
            'total_musicas', 'itens', 'observacoes',
            'created_at', 'updated_at',
        ]


class TempoLiturgicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempoLiturgico
        fields = ['id', 'nome', 'tipo', 'cor_liturgica', 'descricao']


class CelebracaoSerializer(serializers.ModelSerializer):
    tempo_liturgico_nome = serializers.CharField(
        source='tempo_liturgico.nome', read_only=True, default=''
    )
    repertorio_nome = serializers.CharField(
        source='repertorio.nome', read_only=True, default=''
    )
    tem_repertorio = serializers.BooleanField(read_only=True)

    class Meta:
        model = Celebracao
        fields = [
            'id', 'titulo', 'data', 'horario', 'tipo_celebracao',
            'tempo_liturgico', 'tempo_liturgico_nome',
            'local', 'celebrante',
            'repertorio', 'repertorio_nome', 'tem_repertorio',
            'observacoes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
