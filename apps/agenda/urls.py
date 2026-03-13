from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.AgendaView.as_view(), name='agenda'),
    path('celebracoes/', views.CelebracaoListView.as_view(), name='celebracao_list'),
    path('celebracoes/nova/', views.CelebracaoCreateView.as_view(), name='celebracao_create'),
    path('celebracoes/<int:pk>/', views.CelebracaoDetailView.as_view(), name='celebracao_detail'),
    path('celebracoes/<int:pk>/editar/', views.CelebracaoUpdateView.as_view(), name='celebracao_update'),
    path('celebracoes/<int:pk>/excluir/', views.CelebracaoDeleteView.as_view(), name='celebracao_delete'),
]
