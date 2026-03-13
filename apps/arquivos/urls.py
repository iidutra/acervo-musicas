from django.urls import path

from . import views

app_name = 'arquivos'

urlpatterns = [
    # PDF
    path(
        'musica/<int:musica_pk>/pdf/novo/',
        views.PDFArquivoCreateView.as_view(),
        name='pdf_create',
    ),
    path(
        'pdf/<int:pk>/excluir/',
        views.PDFArquivoDeleteView.as_view(),
        name='pdf_delete',
    ),
    # Audio
    path(
        'musica/<int:musica_pk>/audio/novo/',
        views.AudioProprioCreateView.as_view(),
        name='audio_create',
    ),
    path(
        'audio/<int:pk>/excluir/',
        views.AudioProprioDeleteView.as_view(),
        name='audio_delete',
    ),
    # Link Externo
    path(
        'musica/<int:musica_pk>/link/novo/',
        views.LinkExternoCreateView.as_view(),
        name='link_create',
    ),
    path(
        'link/<int:pk>/excluir/',
        views.LinkExternoDeleteView.as_view(),
        name='link_delete',
    ),
    # Cifra
    path(
        'musica/<int:musica_pk>/cifra/nova/',
        views.CifraCreateView.as_view(),
        name='cifra_create',
    ),
    path(
        'cifra/<int:pk>/editar/',
        views.CifraUpdateView.as_view(),
        name='cifra_update',
    ),
    path(
        'cifra/<int:pk>/excluir/',
        views.CifraDeleteView.as_view(),
        name='cifra_delete',
    ),
]
