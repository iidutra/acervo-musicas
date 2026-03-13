import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tests.factories import (
    UserFactory, MusicaFactory, CategoriaLiturgicaFactory,
    TagFactory, RepertorioFactory, CelebracaoFactory,
)


@pytest.fixture
def api_client():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestMusicaAPI:
    def test_list(self, api_client):
        MusicaFactory.create_batch(3)
        response = api_client.get('/api/musicas/')
        assert response.status_code == 200
        assert response.data['count'] == 3

    def test_create(self, api_client):
        response = api_client.post('/api/musicas/', {
            'titulo': 'API Musica',
            'tom_principal': 'C',
        })
        assert response.status_code == 201

    def test_retrieve(self, api_client):
        musica = MusicaFactory()
        response = api_client.get(f'/api/musicas/{musica.pk}/')
        assert response.status_code == 200
        assert response.data['titulo'] == musica.titulo

    def test_update(self, api_client):
        musica = MusicaFactory()
        response = api_client.patch(f'/api/musicas/{musica.pk}/', {
            'titulo': 'Updated',
        })
        assert response.status_code == 200

    def test_toggle_ativo(self, api_client):
        musica = MusicaFactory(ativo=True)
        response = api_client.post(f'/api/musicas/{musica.pk}/toggle_ativo/')
        assert response.status_code == 200
        assert response.data['ativo'] is False

    def test_estatisticas(self, api_client):
        MusicaFactory.create_batch(5)
        response = api_client.get('/api/musicas/estatisticas/')
        assert response.status_code == 200
        assert response.data['total_musicas'] == 5

    def test_filter_by_tom(self, api_client):
        MusicaFactory(tom_principal='C')
        MusicaFactory(tom_principal='G')
        response = api_client.get('/api/musicas/', {'tom_principal': 'C'})
        assert response.data['count'] == 1

    def test_search(self, api_client):
        MusicaFactory(titulo='Aleluia Pascal')
        MusicaFactory(titulo='Santo')
        response = api_client.get('/api/musicas/', {'search': 'Aleluia'})
        assert response.data['count'] == 1

    def test_unauthenticated(self):
        client = APIClient()
        response = client.get('/api/musicas/')
        assert response.status_code in (401, 403)


@pytest.mark.django_db
class TestCategoriaAPI:
    def test_list(self, api_client):
        CategoriaLiturgicaFactory.create_batch(3)
        response = api_client.get('/api/categorias/')
        assert response.status_code == 200

    def test_create(self, api_client):
        response = api_client.post('/api/categorias/', {'nome': 'Nova Cat', 'ordem': 1})
        assert response.status_code == 201


@pytest.mark.django_db
class TestTagAPI:
    def test_list(self, api_client):
        TagFactory.create_batch(3)
        response = api_client.get('/api/tags/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestRepertorioAPI:
    def test_list(self, api_client):
        RepertorioFactory.create_batch(2)
        response = api_client.get('/api/repertorios/')
        assert response.status_code == 200

    def test_detail_with_itens(self, api_client):
        rep = RepertorioFactory()
        response = api_client.get(f'/api/repertorios/{rep.pk}/')
        assert response.status_code == 200
        assert 'itens' in response.data


@pytest.mark.django_db
class TestCelebracaoAPI:
    def test_list(self, api_client):
        CelebracaoFactory.create_batch(2)
        response = api_client.get('/api/celebracoes/')
        assert response.status_code == 200

    def test_create(self, api_client):
        response = api_client.post('/api/celebracoes/', {
            'titulo': 'Missa Teste',
            'data': '2026-03-15',
            'tipo_celebracao': 'missa_dominical',
        })
        assert response.status_code == 201
