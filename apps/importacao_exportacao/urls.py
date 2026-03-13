from django.urls import path
from apps.importacao_exportacao import views

app_name = 'importacao_exportacao'

urlpatterns = [
    path('', views.ImportacaoView.as_view(), name='importar'),
    path('resultado/<int:pk>/', views.ImportacaoResultadoView.as_view(), name='importacao_resultado'),
    path('historico/', views.ImportacaoListView.as_view(), name='importacao_historico'),
    path('exportar/', views.ExportacaoView.as_view(), name='exportar'),
]
