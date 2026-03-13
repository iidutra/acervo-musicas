from django.urls import path

from apps.repertorios import views

app_name = 'repertorios'

urlpatterns = [
    path('', views.RepertorioListView.as_view(), name='repertorio_list'),
    path('novo/', views.RepertorioCreateView.as_view(), name='repertorio_create'),
    path('<int:pk>/', views.RepertorioDetailView.as_view(), name='repertorio_detail'),
    path('<int:pk>/editar/', views.RepertorioUpdateView.as_view(), name='repertorio_update'),
    path('<int:pk>/excluir/', views.RepertorioDeleteView.as_view(), name='repertorio_delete'),
    path('<int:pk>/imprimir/', views.RepertorioExportView.as_view(), name='repertorio_print'),
    path('recomendacao/', views.RecomendacaoView.as_view(), name='recomendacao'),
]
