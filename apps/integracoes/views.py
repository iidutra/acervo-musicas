import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from apps.arquivos.models import Cifra, LinkExterno
from apps.integracoes.search_service import buscar_cifra, buscar_letra, buscar_youtube
from apps.musicas.models import Musica


class PesquisarView(LoginRequiredMixin, View):
    """Pesquisa de músicas no YouTube, letras e cifras."""

    template_name = 'integracoes/pesquisar.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        context = {
            'query': query,
            'videos': [],
            'letra_result': None,
            'cifra_result': None,
        }

        if query:
            context['videos'] = buscar_youtube(query, limit=6)
            context['letra_result'] = buscar_letra(query)
            context['cifra_result'] = buscar_cifra(query)

        return render(request, self.template_name, context)


class SalvarPesquisaView(LoginRequiredMixin, View):
    """Salva música pesquisada no acervo."""

    def post(self, request):
        titulo = request.POST.get('titulo', '').strip()
        letra = request.POST.get('letra', '').strip()
        artista = request.POST.get('artista', '').strip()
        cifra_texto = request.POST.get('cifra_texto', '').strip()
        tom = request.POST.get('tom', '').strip()
        videos_json = request.POST.get('videos_selecionados', '[]')

        if not titulo:
            messages.error(request, 'Informe um título para a música.')
            return redirect('integracoes:pesquisar')

        # Create the song
        musica = Musica.objects.create(
            titulo=titulo,
            subtitulo=artista,
            letra=letra,
            tom_principal=tom if tom else 'NI',
        )

        # Create cifra if provided
        if cifra_texto:
            Cifra.objects.create(
                musica=musica,
                tipo_cifra='texto',
                conteudo_texto=cifra_texto,
                tom=tom if tom else '',
            )

        # Create links for selected videos
        try:
            videos = json.loads(videos_json)
        except (json.JSONDecodeError, TypeError):
            videos = []

        for video in videos:
            if isinstance(video, dict) and video.get('url'):
                LinkExterno.objects.create(
                    musica=musica,
                    url=video['url'],
                    tipo_conteudo='video',
                    provider='youtube',
                    titulo_externo=video.get('titulo', ''),
                    thumbnail_url=video.get('thumbnail', ''),
                    embed_url=f"https://www.youtube.com/embed/{video.get('video_id', '')}",
                )

        parts = [f'Música "{titulo}" salva com sucesso!']
        if cifra_texto:
            parts.append('Cifra incluída.')
        if videos:
            parts.append(f'{len(videos)} vídeo(s) vinculado(s).')
        messages.success(request, ' '.join(parts))
        return redirect('musicas:musica_detail', pk=musica.pk)
