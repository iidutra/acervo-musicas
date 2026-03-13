from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.template.response import TemplateResponse

from apps.repertorios.forms import RepertorioForm, RepertorioMusicaFormSet
from apps.repertorios.models import Repertorio


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

class RepertorioListView(LoginRequiredMixin, ListView):
    model = Repertorio
    template_name = 'repertorios/repertorio_list.html'
    context_object_name = 'repertorios'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            qs = qs.filter(Q(nome__icontains=search))
        tipo = self.request.GET.get('tipo_celebracao', '').strip()
        if tipo:
            qs = qs.filter(tipo_celebracao=tipo)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['tipo_celebracao'] = self.request.GET.get('tipo_celebracao', '')
        from apps.core.choices import TIPO_CELEBRACAO_CHOICES
        ctx['tipo_celebracao_choices'] = TIPO_CELEBRACAO_CHOICES
        return ctx


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

class RepertorioDetailView(LoginRequiredMixin, DetailView):
    model = Repertorio
    template_name = 'repertorios/repertorio_detail.html'
    context_object_name = 'repertorio'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['itens'] = (
            self.object.itens
            .select_related('musica', 'categoria_no_repertorio')
            .order_by('ordem')
        )
        return ctx


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class RepertorioCreateView(LoginRequiredMixin, CreateView):
    model = Repertorio
    form_class = RepertorioForm
    template_name = 'repertorios/repertorio_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = RepertorioMusicaFormSet(
                self.request.POST, instance=self.object
            )
        else:
            ctx['formset'] = RepertorioMusicaFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('repertorios:repertorio_detail', kwargs={'pk': self.object.pk})


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class RepertorioUpdateView(LoginRequiredMixin, UpdateView):
    model = Repertorio
    form_class = RepertorioForm
    template_name = 'repertorios/repertorio_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = RepertorioMusicaFormSet(
                self.request.POST, instance=self.object
            )
        else:
            ctx['formset'] = RepertorioMusicaFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('repertorios:repertorio_detail', kwargs={'pk': self.object.pk})


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class RepertorioDeleteView(LoginRequiredMixin, DeleteView):
    model = Repertorio
    template_name = 'repertorios/repertorio_confirm_delete.html'
    context_object_name = 'repertorio'
    success_url = reverse_lazy('repertorios:repertorio_list')


# ---------------------------------------------------------------------------
# Export / Print
# ---------------------------------------------------------------------------

class RepertorioExportView(LoginRequiredMixin, View):
    """Render a printer-friendly HTML page for a single repertoire."""

    def get(self, request, pk):
        repertorio = Repertorio.objects.get(pk=pk)
        itens = (
            repertorio.itens
            .select_related('musica', 'categoria_no_repertorio')
            .order_by('ordem')
        )
        return TemplateResponse(
            request,
            'repertorios/repertorio_print.html',
            {
                'repertorio': repertorio,
                'itens': itens,
            },
        )


# ---------------------------------------------------------------------------
# Recomendação
# ---------------------------------------------------------------------------

class RecomendacaoView(LoginRequiredMixin, View):
    """View para obter recomendações de repertório."""

    def get(self, request):
        from apps.repertorios.services import RecomendacaoService
        from apps.core.choices import TIPO_CELEBRACAO_CHOICES
        from apps.agenda.choices import TEMPO_LITURGICO_CHOICES

        tipo = request.GET.get('tipo_celebracao', 'missa_dominical')
        tempo = request.GET.get('tempo_liturgico', '')

        service = RecomendacaoService()
        recomendacoes = service.recomendar_repertorio_completo(
            tipo_celebracao=tipo,
            tempo_liturgico=tempo,
        )

        return TemplateResponse(
            request,
            'repertorios/recomendacao.html',
            {
                'recomendacoes': recomendacoes,
                'tipo_celebracao': tipo,
                'tempo_liturgico': tempo,
                'tipo_celebracao_choices': TIPO_CELEBRACAO_CHOICES,
                'tempo_liturgico_choices': TEMPO_LITURGICO_CHOICES,
            },
        )
