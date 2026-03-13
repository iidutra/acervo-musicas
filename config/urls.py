"""
URL configuration for Acervo Liturgico Digital project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('musicas/', include('apps.musicas.urls')),
    path('arquivos/', include('apps.arquivos.urls')),
    path('repertorios/', include('apps.repertorios.urls')),
    path('importacao-exportacao/', include('apps.importacao_exportacao.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('apps.api.urls')),
    path('agenda/', include('apps.agenda.urls')),
    path('integracoes/', include('apps.integracoes.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar  # noqa: F401
        urlpatterns = [
            path('__debug__/', include('debug_toolbar.urls')),
        ] + urlpatterns
    except ImportError:
        pass
