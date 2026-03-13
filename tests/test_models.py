import pytest
from tests.factories import (
    MusicaFactory, CategoriaLiturgicaFactory, TagFactory,
    RepertorioFactory, RepertorioMusicaFactory, CelebracaoFactory,
)


@pytest.mark.django_db
class TestMusica:
    def test_create(self):
        musica = MusicaFactory(titulo='Santo', tom_principal='G')
        assert musica.titulo == 'Santo'
        assert musica.tom_principal == 'G'
        assert musica.ativo is True

    def test_str(self):
        musica = MusicaFactory(titulo='Aleluia')
        assert str(musica) == 'Aleluia'

    def test_tom_normalizado_auto(self):
        musica = MusicaFactory(tom_principal='C')
        assert musica.tom_normalizado == 'C'

    def test_tom_ni(self):
        musica = MusicaFactory(tom_principal='NI')
        assert musica.tom_normalizado == ''

    def test_categorias_m2m(self):
        cat = CategoriaLiturgicaFactory(nome='Entrada')
        musica = MusicaFactory(categorias=[cat])
        assert cat in musica.categorias.all()

    def test_tags_m2m(self):
        tag = TagFactory(nome='Jovens')
        musica = MusicaFactory(tags=[tag])
        assert tag in musica.tags.all()

    def test_tem_pdf_false(self):
        musica = MusicaFactory()
        assert musica.tem_pdf is False

    def test_tem_audio_false(self):
        musica = MusicaFactory()
        assert musica.tem_audio is False


@pytest.mark.django_db
class TestCategoriaLiturgica:
    def test_create(self):
        cat = CategoriaLiturgicaFactory(nome='Comunhão')
        assert cat.nome == 'Comunhão'
        assert cat.ativo is True

    def test_str(self):
        cat = CategoriaLiturgicaFactory(nome='Ofertório')
        assert str(cat) == 'Ofertório'

    def test_ordering(self):
        cat2 = CategoriaLiturgicaFactory(nome='B', ordem=2)
        cat1 = CategoriaLiturgicaFactory(nome='A', ordem=1)
        from apps.musicas.models import CategoriaLiturgica
        cats = list(CategoriaLiturgica.objects.all())
        assert cats[0].ordem <= cats[1].ordem


@pytest.mark.django_db
class TestTag:
    def test_create(self):
        tag = TagFactory(nome='Eucaristia')
        assert tag.nome == 'Eucaristia'

    def test_str(self):
        tag = TagFactory(nome='Retiro')
        assert str(tag) == 'Retiro'


@pytest.mark.django_db
class TestRepertorio:
    def test_create(self):
        rep = RepertorioFactory(nome='Missa Domingo')
        assert rep.nome == 'Missa Domingo'

    def test_total_musicas(self):
        rep = RepertorioFactory()
        assert rep.total_musicas == 0

    def test_total_musicas_with_items(self):
        rep = RepertorioFactory()
        RepertorioMusicaFactory(repertorio=rep)
        RepertorioMusicaFactory(repertorio=rep)
        assert rep.total_musicas == 2


@pytest.mark.django_db
class TestRepertorioMusica:
    def test_tom_efetivo_uses_repertorio_tom(self):
        item = RepertorioMusicaFactory(tom_no_repertorio='D')
        assert item.tom_efetivo == 'D'

    def test_tom_efetivo_fallback_to_musica(self):
        musica = MusicaFactory(tom_principal='G')
        item = RepertorioMusicaFactory(musica=musica, tom_no_repertorio='')
        assert item.tom_efetivo == 'G'


@pytest.mark.django_db
class TestCelebracao:
    def test_create(self):
        cel = CelebracaoFactory(titulo='Missa 1')
        assert cel.titulo == 'Missa 1'

    def test_tem_repertorio_false(self):
        cel = CelebracaoFactory()
        assert cel.tem_repertorio is False

    def test_tem_repertorio_true(self):
        rep = RepertorioFactory()
        cel = CelebracaoFactory(repertorio=rep)
        assert cel.tem_repertorio is True
