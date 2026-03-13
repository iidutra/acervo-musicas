from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from apps.musicas.models import Musica
from apps.importacao_exportacao.forms import ExportacaoForm, ImportacaoForm
from apps.importacao_exportacao.models import ImportacaoLote
from apps.importacao_exportacao.services import ExportService, ImportService


class ImportacaoView(LoginRequiredMixin, FormView):
    """View para upload e processamento de importação."""

    template_name = 'importacao_exportacao/importar.html'
    form_class = ImportacaoForm

    def form_valid(self, form):
        arquivo = form.cleaned_data['arquivo']
        tipo = form.cleaned_data['tipo_importacao']

        lote = ImportacaoLote.objects.create(
            tipo_importacao=tipo,
            nome_arquivo=arquivo.name,
            arquivo=arquivo,
        )

        service = ImportService()
        metodo_map = {
            'csv': service.importar_csv,
            'excel': service.importar_excel,
            'json': service.importar_json,
            'zip': service.importar_zip,
        }

        metodo = metodo_map.get(tipo)
        if metodo:
            # Reopen the saved file for processing
            lote.arquivo.open('rb')
            try:
                lote = metodo(lote.arquivo, lote)
            finally:
                lote.arquivo.close()

        return redirect('importacao_exportacao:importacao_resultado', pk=lote.pk)


class ImportacaoResultadoView(LoginRequiredMixin, DetailView):
    """View para exibir resultado de uma importação."""

    model = ImportacaoLote
    template_name = 'importacao_exportacao/importacao_resultado.html'
    context_object_name = 'lote'


class ImportacaoListView(LoginRequiredMixin, ListView):
    """View para listar histórico de importações."""

    model = ImportacaoLote
    template_name = 'importacao_exportacao/importacao_historico.html'
    context_object_name = 'lotes'
    paginate_by = 20


class ExportacaoView(LoginRequiredMixin, FormView):
    """View para exportação de músicas."""

    template_name = 'importacao_exportacao/exportar.html'
    form_class = ExportacaoForm

    def form_valid(self, form):
        formato = form.cleaned_data['formato']
        incluir_midias = form.cleaned_data.get('incluir_midias', False)
        filtro_ativo = form.cleaned_data.get('filtro_ativo', 'todos')

        queryset = Musica.objects.all()
        if filtro_ativo == 'ativos':
            queryset = queryset.filter(ativo=True)
        elif filtro_ativo == 'inativos':
            queryset = queryset.filter(ativo=False)

        service = ExportService()

        if formato == 'csv':
            return service.exportar_csv(queryset)
        elif formato == 'excel':
            return service.exportar_excel(queryset)
        elif formato == 'json':
            return service.exportar_json(queryset)
        elif formato == 'zip':
            return service.exportar_zip(queryset, incluir_midias=incluir_midias)

        return redirect('importacao_exportacao:exportar')
