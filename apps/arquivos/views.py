import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from apps.musicas.models import Musica
from .forms import PDFArquivoForm, AudioProprioForm, LinkExternoForm, CifraForm
from .models import PDFArquivo, AudioProprio, LinkExterno, Cifra
from .services import extrair_texto_pdf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mixin: inject musica from URL kwargs
# ---------------------------------------------------------------------------
class MusicaMixin(LoginRequiredMixin):
    """Mixin that fetches the Musica instance from URL kwargs."""

    def get_musica(self):
        if not hasattr(self, '_musica'):
            self._musica = get_object_or_404(
                Musica, pk=self.kwargs['musica_pk']
            )
        return self._musica

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['musica'] = self.get_musica()
        return ctx

    def get_success_url(self):
        return reverse(
            'musicas:musica_detail',
            kwargs={'pk': self.get_musica().pk},
        )


class ArquivoDeleteMixin(LoginRequiredMixin):
    """Mixin for delete views that redirect back to the musica detail."""

    def get_success_url(self):
        return reverse(
            'musicas:musica_detail',
            kwargs={'pk': self.object.musica_id},
        )


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
class PDFArquivoCreateView(MusicaMixin, CreateView):
    model = PDFArquivo
    form_class = PDFArquivoForm
    template_name = 'arquivos/pdf_form.html'

    def form_valid(self, form):
        form.instance.musica = self.get_musica()
        response = super().form_valid(form)

        # Attempt async-safe text extraction after save
        try:
            obj = self.object
            if obj.arquivo:
                texto = extrair_texto_pdf(
                    obj.arquivo.path,
                    pagina_inicial=obj.pagina_inicial,
                    pagina_final=obj.pagina_final,
                )
                if texto:
                    obj.texto_extraido = texto
                    obj.save(update_fields=['texto_extraido'])
        except Exception as exc:
            logger.warning('Falha na extracao de texto do PDF %s: %s', self.object.pk, exc)

        messages.success(self.request, 'PDF adicionado com sucesso.')
        return response


class PDFArquivoDeleteView(ArquivoDeleteMixin, DeleteView):
    model = PDFArquivo
    template_name = 'arquivos/confirm_delete.html'
    context_object_name = 'pdf'

    def form_valid(self, form):
        messages.success(self.request, 'PDF removido com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
class AudioProprioCreateView(MusicaMixin, CreateView):
    model = AudioProprio
    form_class = AudioProprioForm
    template_name = 'arquivos/audio_form.html'

    def form_valid(self, form):
        form.instance.musica = self.get_musica()
        messages.success(self.request, 'Audio adicionado com sucesso.')
        return super().form_valid(form)


class AudioProprioDeleteView(ArquivoDeleteMixin, DeleteView):
    model = AudioProprio
    template_name = 'arquivos/confirm_delete.html'
    context_object_name = 'audio'

    def form_valid(self, form):
        messages.success(self.request, 'Audio removido com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Link Externo
# ---------------------------------------------------------------------------
class LinkExternoCreateView(MusicaMixin, CreateView):
    model = LinkExterno
    form_class = LinkExternoForm
    template_name = 'arquivos/link_form.html'

    def form_valid(self, form):
        form.instance.musica = self.get_musica()
        messages.success(self.request, 'Link externo adicionado com sucesso.')
        return super().form_valid(form)


class LinkExternoDeleteView(ArquivoDeleteMixin, DeleteView):
    model = LinkExterno
    template_name = 'arquivos/confirm_delete.html'
    context_object_name = 'link'

    def form_valid(self, form):
        messages.success(self.request, 'Link externo removido com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Cifra
# ---------------------------------------------------------------------------
class CifraCreateView(MusicaMixin, CreateView):
    model = Cifra
    form_class = CifraForm
    template_name = 'arquivos/cifra_form.html'

    def form_valid(self, form):
        form.instance.musica = self.get_musica()
        messages.success(self.request, 'Cifra adicionada com sucesso.')
        return super().form_valid(form)


class CifraUpdateView(LoginRequiredMixin, UpdateView):
    model = Cifra
    form_class = CifraForm
    template_name = 'arquivos/cifra_form.html'
    context_object_name = 'cifra'

    def get_success_url(self):
        return reverse(
            'musicas:musica_detail',
            kwargs={'pk': self.object.musica_id},
        )

    def form_valid(self, form):
        messages.success(self.request, 'Cifra atualizada com sucesso.')
        return super().form_valid(form)


class CifraDeleteView(ArquivoDeleteMixin, DeleteView):
    model = Cifra
    template_name = 'arquivos/confirm_delete.html'
    context_object_name = 'cifra'

    def form_valid(self, form):
        messages.success(self.request, 'Cifra removida com sucesso.')
        return super().form_valid(form)
