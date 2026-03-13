import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CelebracaoForm, CelebracaoFiltroForm
from .models import Celebracao


class AgendaView(LoginRequiredMixin, ListView):
    """Visão de calendário mensal das celebrações."""
    model = Celebracao
    template_name = 'agenda/agenda.html'
    context_object_name = 'celebracoes'

    def get_month_year(self):
        today = date.today()
        try:
            mes = int(self.request.GET.get('mes', today.month))
            ano = int(self.request.GET.get('ano', today.year))
        except (ValueError, TypeError):
            mes, ano = today.month, today.year
        return mes, ano

    def get_queryset(self):
        mes, ano = self.get_month_year()
        qs = Celebracao.objects.filter(data__year=ano, data__month=mes)
        tipo = self.request.GET.get('tipo_celebracao', '')
        if tipo:
            qs = qs.filter(tipo_celebracao=tipo)
        return qs.select_related('tempo_liturgico', 'repertorio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mes, ano = self.get_month_year()

        # Calendar data
        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        month_days = cal.monthdayscalendar(ano, mes)

        # Map celebrations to days
        celebracoes_por_dia = {}
        for cel in ctx['celebracoes']:
            dia = cel.data.day
            celebracoes_por_dia.setdefault(dia, []).append(cel)

        # Build calendar weeks with celebration data
        weeks = []
        for week in month_days:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': 0, 'celebracoes': []})
                else:
                    week_data.append({
                        'day': day,
                        'celebracoes': celebracoes_por_dia.get(day, []),
                        'is_today': day == date.today().day and mes == date.today().month and ano == date.today().year,
                    })
            weeks.append(week_data)

        ctx['weeks'] = weeks
        ctx['mes'] = mes
        ctx['ano'] = ano
        ctx['nome_mes'] = calendar.month_name[mes].capitalize()
        ctx['filtro_form'] = CelebracaoFiltroForm(self.request.GET)

        # Navigation
        if mes == 1:
            ctx['prev_mes'], ctx['prev_ano'] = 12, ano - 1
        else:
            ctx['prev_mes'], ctx['prev_ano'] = mes - 1, ano
        if mes == 12:
            ctx['next_mes'], ctx['next_ano'] = 1, ano + 1
        else:
            ctx['next_mes'], ctx['next_ano'] = mes + 1, ano

        return ctx


class CelebracaoListView(LoginRequiredMixin, ListView):
    """Lista linear de celebrações (próximas primeiro)."""
    model = Celebracao
    template_name = 'agenda/celebracao_list.html'
    context_object_name = 'celebracoes'
    paginate_by = 20

    def get_queryset(self):
        return Celebracao.objects.select_related(
            'tempo_liturgico', 'repertorio'
        ).order_by('data', 'horario')


class CelebracaoDetailView(LoginRequiredMixin, DetailView):
    model = Celebracao
    template_name = 'agenda/celebracao_detail.html'
    context_object_name = 'celebracao'

    def get_queryset(self):
        return Celebracao.objects.select_related('tempo_liturgico', 'repertorio')


class CelebracaoCreateView(LoginRequiredMixin, CreateView):
    model = Celebracao
    form_class = CelebracaoForm
    template_name = 'agenda/celebracao_form.html'
    success_url = reverse_lazy('agenda:agenda')

    def form_valid(self, form):
        messages.success(self.request, 'Celebração criada com sucesso!')
        return super().form_valid(form)


class CelebracaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Celebracao
    form_class = CelebracaoForm
    template_name = 'agenda/celebracao_form.html'
    success_url = reverse_lazy('agenda:agenda')

    def form_valid(self, form):
        messages.success(self.request, 'Celebração atualizada com sucesso!')
        return super().form_valid(form)


class CelebracaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Celebracao
    template_name = 'agenda/celebracao_confirm_delete.html'
    context_object_name = 'celebracao'
    success_url = reverse_lazy('agenda:agenda')
