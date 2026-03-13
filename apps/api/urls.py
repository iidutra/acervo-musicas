from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'musicas', views.MusicaViewSet)
router.register(r'categorias', views.CategoriaLiturgicaViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'pdfs', views.PDFArquivoViewSet)
router.register(r'audios', views.AudioProprioViewSet)
router.register(r'links', views.LinkExternoViewSet)
router.register(r'cifras', views.CifraViewSet)
router.register(r'repertorios', views.RepertorioViewSet)
router.register(r'repertorio-musicas', views.RepertorioMusicaViewSet)
router.register(r'tempos-liturgicos', views.TempoLiturgicoViewSet)
router.register(r'celebracoes', views.CelebracaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='api_token'),
]
