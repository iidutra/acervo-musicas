import pytest
from django.urls import reverse
from tests.factories import (
    UserFactory, MusicaFactory, CategoriaLiturgicaFactory,
    RepertorioFactory, CelebracaoFactory,
)


@pytest.mark.django_db
class TestDashboard:
    def test_redirect_if_not_logged_in(self, client):
        response = client.get(reverse('core:dashboard'))
        assert response.status_code == 302

    def test_dashboard_ok(self, auth_client):
        response = auth_client.get(reverse('core:dashboard'))
        assert response.status_code == 200

    def test_dashboard_context(self, auth_client):
        MusicaFactory.create_batch(3)
        response = auth_client.get(reverse('core:dashboard'))
        assert response.context['total_musicas'] == 3


@pytest.mark.django_db
class TestMusicaViews:
    def test_list(self, auth_client):
        MusicaFactory.create_batch(5)
        response = auth_client.get(reverse('musicas:musica_list'))
        assert response.status_code == 200

    def test_list_filter_by_tom(self, auth_client):
        MusicaFactory(tom_principal='C')
        MusicaFactory(tom_principal='G')
        response = auth_client.get(reverse('musicas:musica_list'), {'tom': 'C'})
        assert response.status_code == 200

    def test_detail(self, auth_client):
        musica = MusicaFactory()
        response = auth_client.get(reverse('musicas:musica_detail', kwargs={'pk': musica.pk}))
        assert response.status_code == 200

    def test_create_get(self, auth_client):
        response = auth_client.get(reverse('musicas:musica_create'))
        assert response.status_code == 200

    def test_create_post(self, auth_client):
        response = auth_client.post(reverse('musicas:musica_create'), {
            'titulo': 'Nova Música',
            'tom_principal': 'Am',
            'origem': 'manual',
            'ativo': True,
        })
        assert response.status_code == 302
        from apps.musicas.models import Musica
        assert Musica.objects.filter(titulo='Nova Música').exists()

    def test_update(self, auth_client):
        musica = MusicaFactory()
        response = auth_client.post(
            reverse('musicas:musica_update', kwargs={'pk': musica.pk}),
            {
                'titulo': 'Atualizada',
                'tom_principal': 'D',
                'origem': 'manual',
                'ativo': True,
            },
        )
        assert response.status_code == 302
        musica.refresh_from_db()
        assert musica.titulo == 'Atualizada'

    def test_toggle_ativo(self, auth_client):
        musica = MusicaFactory(ativo=True)
        response = auth_client.post(
            reverse('musicas:musica_toggle_ativo', kwargs={'pk': musica.pk})
        )
        assert response.status_code == 302
        musica.refresh_from_db()
        assert musica.ativo is False


@pytest.mark.django_db
class TestRepertorioViews:
    def test_list(self, auth_client):
        response = auth_client.get(reverse('repertorios:repertorio_list'))
        assert response.status_code == 200

    def test_detail(self, auth_client):
        rep = RepertorioFactory()
        response = auth_client.get(reverse('repertorios:repertorio_detail', kwargs={'pk': rep.pk}))
        assert response.status_code == 200


@pytest.mark.django_db
class TestAgendaViews:
    def test_agenda(self, auth_client):
        response = auth_client.get(reverse('agenda:agenda'))
        assert response.status_code == 200

    def test_celebracao_create_get(self, auth_client):
        response = auth_client.get(reverse('agenda:celebracao_create'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestImportExportViews:
    def test_importar_page(self, auth_client):
        response = auth_client.get(reverse('importacao_exportacao:importar'))
        assert response.status_code == 200

    def test_exportar_page(self, auth_client):
        response = auth_client.get(reverse('importacao_exportacao:exportar'))
        assert response.status_code == 200

    def test_historico_page(self, auth_client):
        response = auth_client.get(reverse('importacao_exportacao:importacao_historico'))
        assert response.status_code == 200
