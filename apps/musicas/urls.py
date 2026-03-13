from django.urls import path
from . import views

app_name = 'musicas'

urlpatterns = [
    # Músicas
    path('', views.MusicaListView.as_view(), name='musica_list'),
    path('nova/', views.MusicaCreateView.as_view(), name='musica_create'),
    path('<int:pk>/', views.MusicaDetailView.as_view(), name='musica_detail'),
    path('<int:pk>/editar/', views.MusicaUpdateView.as_view(), name='musica_update'),
    path('<int:pk>/toggle-ativo/', views.MusicaToggleAtivoView.as_view(), name='musica_toggle_ativo'),

    # Categorias Litúrgicas
    path('categorias/', views.CategoriaLiturgicaListView.as_view(), name='categoria_list'),
    path('categorias/nova/', views.CategoriaLiturgicaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaLiturgicaUpdateView.as_view(), name='categoria_update'),

    # Tags
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/nova/', views.TagCreateView.as_view(), name='tag_create'),
    path('tags/<int:pk>/editar/', views.TagUpdateView.as_view(), name='tag_update'),
]
