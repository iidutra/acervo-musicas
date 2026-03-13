from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import (
    MusicaForm,
    MusicaFiltroForm,
    CategoriaLiturgicaForm,
    TagForm,
)
from .models import Musica, CategoriaLiturgica, Tag


# ---------------------------------------------------------------------------
# Música views
# ---------------------------------------------------------------------------

class MusicaListView(LoginRequiredMixin, ListView):
    model = Musica
    template_name = 'musicas/musica_list.html'
    context_object_name = 'musicas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related().prefetch_related(
            'categorias', 'tags'
        )
        self.filtro_form = MusicaFiltroForm(self.request.GET or None)

        if self.filtro_form.is_valid():
            busca = self.filtro_form.cleaned_data.get('busca')
            tom = self.filtro_form.cleaned_data.get('tom')
            categoria = self.filtro_form.cleaned_data.get('categoria')
            tag = self.filtro_form.cleaned_data.get('tag')
            tem_pdf = self.filtro_form.cleaned_data.get('tem_pdf')
            tem_audio = self.filtro_form.cleaned_data.get('tem_audio')
            tem_cifra = self.filtro_form.cleaned_data.get('tem_cifra')
            ativo = self.filtro_form.cleaned_data.get('ativo')

            if busca:
                qs = qs.filter(
                    Q(titulo__icontains=busca)
                    | Q(subtitulo__icontains=busca)
                    | Q(letra__icontains=busca)
                )

            if tom:
                qs = qs.filter(tom_principal=tom)

            if categoria:
                qs = qs.filter(categorias=categoria)

            if tag:
                qs = qs.filter(tags=tag)

            if tem_pdf:
                qs = qs.filter(pdfs__isnull=False).distinct()

            if tem_audio:
                qs = qs.filter(audios__isnull=False).distinct()

            if tem_cifra:
                qs = qs.filter(cifras__isnull=False).distinct()

            if ativo == 'ativo':
                qs = qs.filter(ativo=True)
            elif ativo == 'inativo':
                qs = qs.filter(ativo=False)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = self.filtro_form
        context['total_resultados'] = self.get_queryset().count()
        return context


class MusicaDetailView(LoginRequiredMixin, DetailView):
    model = Musica
    template_name = 'musicas/musica_detail.html'
    context_object_name = 'musica'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'categorias', 'tags'
        )


class MusicaCreateView(LoginRequiredMixin, CreateView):
    model = Musica
    form_class = MusicaForm
    template_name = 'musicas/musica_form.html'
    success_url = reverse_lazy('musicas:musica_list')

    def form_valid(self, form):
        messages.success(self.request, 'Música criada com sucesso!')
        return super().form_valid(form)


class MusicaUpdateView(LoginRequiredMixin, UpdateView):
    model = Musica
    form_class = MusicaForm
    template_name = 'musicas/musica_form.html'
    success_url = reverse_lazy('musicas:musica_list')

    def form_valid(self, form):
        messages.success(self.request, 'Música atualizada com sucesso!')
        return super().form_valid(form)


class MusicaToggleAtivoView(LoginRequiredMixin, View):
    """Toggle the 'ativo' flag on a Musica instance (POST only)."""

    def post(self, request, pk):
        musica = get_object_or_404(Musica, pk=pk)
        musica.ativo = not musica.ativo
        musica.save(update_fields=['ativo', 'updated_at'])
        status = 'ativada' if musica.ativo else 'desativada'
        messages.success(request, f'Música "{musica.titulo}" {status} com sucesso!')
        return redirect('musicas:musica_list')

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


# ---------------------------------------------------------------------------
# CategoriaLiturgica views
# ---------------------------------------------------------------------------

class CategoriaLiturgicaListView(LoginRequiredMixin, ListView):
    model = CategoriaLiturgica
    template_name = 'musicas/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 20


class CategoriaLiturgicaCreateView(LoginRequiredMixin, CreateView):
    model = CategoriaLiturgica
    form_class = CategoriaLiturgicaForm
    template_name = 'musicas/categoria_form.html'
    success_url = reverse_lazy('musicas:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoriaLiturgicaUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoriaLiturgica
    form_class = CategoriaLiturgicaForm
    template_name = 'musicas/categoria_form.html'
    success_url = reverse_lazy('musicas:categoria_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Tag views
# ---------------------------------------------------------------------------

class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'musicas/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 20


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'musicas/tag_form.html'
    success_url = reverse_lazy('musicas:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tag criada com sucesso!')
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'musicas/tag_form.html'
    success_url = reverse_lazy('musicas:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tag atualizada com sucesso!')
        return super().form_valid(form)
