from django.apps import AppConfig


class IntegracoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integracoes'
    verbose_name = 'Integrações'

    def ready(self):
        import apps.integracoes.signals  # noqa: F401
