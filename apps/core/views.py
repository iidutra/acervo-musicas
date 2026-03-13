from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.musicas.models import Musica
from apps.arquivos.models import PDFArquivo, AudioProprio
from apps.repertorios.models import Repertorio
from apps.importacao_exportacao.models import ImportacaoLote


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Totals
        context['total_musicas'] = Musica.objects.filter(ativo=True).count()
        context['total_pdfs'] = PDFArquivo.objects.count()
        context['total_audios'] = AudioProprio.objects.count()
        context['total_repertorios'] = Repertorio.objects.count()

        # Recent items
        context['ultimas_musicas'] = (
            Musica.objects.filter(ativo=True)
            .order_by('-created_at')[:10]
        )
        context['ultimos_lotes'] = (
            ImportacaoLote.objects.order_by('-created_at')[:5]
        )

        return context
