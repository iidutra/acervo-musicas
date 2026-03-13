from django.urls import path

from . import views

app_name = 'integracoes'

urlpatterns = [
    path('pesquisar/', views.PesquisarView.as_view(), name='pesquisar'),
    path('pesquisar/salvar/', views.SalvarPesquisaView.as_view(), name='salvar_pesquisa'),
]
