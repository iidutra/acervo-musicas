"""Factories para criação de dados de teste."""
import factory
from django.contrib.auth.models import User
from apps.musicas.models import Musica, CategoriaLiturgica, Tag
from apps.arquivos.models import PDFArquivo, AudioProprio, LinkExterno, Cifra
from apps.repertorios.models import Repertorio, RepertorioMusica
from apps.agenda.models import Celebracao, TempoLiturgico


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class CategoriaLiturgicaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoriaLiturgica
    nome = factory.Sequence(lambda n: f'Categoria {n}')
    ordem = factory.Sequence(lambda n: n)
    ativo = True


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
    nome = factory.Sequence(lambda n: f'Tag {n}')


class MusicaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Musica
    titulo = factory.Sequence(lambda n: f'Música {n}')
    tom_principal = 'C'
    ativo = True

    @factory.post_generation
    def categorias(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.categorias.add(*extracted)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.tags.add(*extracted)


class RepertorioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Repertorio
    nome = factory.Sequence(lambda n: f'Repertório {n}')
    tipo_celebracao = 'missa_dominical'
    data_celebracao = factory.LazyFunction(lambda: __import__('datetime').date.today())


class RepertorioMusicaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RepertorioMusica
    repertorio = factory.SubFactory(RepertorioFactory)
    musica = factory.SubFactory(MusicaFactory)
    ordem = factory.Sequence(lambda n: n)


class LinkExternoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LinkExterno
    musica = factory.SubFactory(MusicaFactory)
    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    provider = 'youtube'
    tipo_conteudo = 'video'


class TempoLiturgicoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TempoLiturgico
    nome = factory.Sequence(lambda n: f'Tempo {n}')
    tipo = 'tempo_comum_1'


class CelebracaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Celebracao
    titulo = factory.Sequence(lambda n: f'Celebração {n}')
    data = factory.LazyFunction(lambda: __import__('datetime').date.today())
    tipo_celebracao = 'missa_dominical'
