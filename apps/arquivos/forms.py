import re
from urllib.parse import urlparse

from django import forms

from .models import PDFArquivo, AudioProprio, LinkExterno, Cifra


# ---------------------------------------------------------------------------
# Tailwind CSS widget classes
# ---------------------------------------------------------------------------
TEXT_CSS = (
    'w-full px-3 py-2 border border-gray-300 rounded-md '
    'focus:outline-none focus:ring-2 focus:ring-blue-500'
)
FILE_CSS = (
    'w-full px-3 py-2 border border-gray-300 rounded-md '
    'file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 '
    'file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
)
SELECT_CSS = TEXT_CSS
TEXTAREA_CSS = TEXT_CSS


def _tw(widget_class, css=None, **extra_attrs):
    """Return a widget instance with Tailwind classes pre-applied."""
    attrs = {'class': css or TEXT_CSS}
    attrs.update(extra_attrs)
    return widget_class(attrs=attrs)


# ---------------------------------------------------------------------------
# PDFArquivoForm
# ---------------------------------------------------------------------------
class PDFArquivoForm(forms.ModelForm):
    class Meta:
        model = PDFArquivo
        exclude = ['musica']
        widgets = {
            'nome': _tw(forms.TextInput, placeholder='Ex: Partitura Piano'),
            'arquivo': _tw(forms.ClearableFileInput, css=FILE_CSS, accept='.pdf'),
            'pagina_inicial': _tw(forms.NumberInput, placeholder='1'),
            'pagina_final': _tw(forms.NumberInput, placeholder='10'),
            'texto_extraido': _tw(forms.Textarea, css=TEXTAREA_CSS, rows='4'),
            'origem': _tw(forms.TextInput, placeholder='upload'),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            ext = arquivo.name.rsplit('.', 1)[-1].lower() if '.' in arquivo.name else ''
            if ext != 'pdf':
                raise forms.ValidationError(
                    'Somente arquivos PDF sao permitidos.'
                )
            # Limit 50 MB
            if arquivo.size > 50 * 1024 * 1024:
                raise forms.ValidationError(
                    'O arquivo PDF nao pode exceder 50 MB.'
                )
        return arquivo

    def clean(self):
        cleaned = super().clean()
        pi = cleaned.get('pagina_inicial')
        pf = cleaned.get('pagina_final')
        if pi and pf and pi > pf:
            raise forms.ValidationError(
                'A pagina inicial deve ser menor ou igual a pagina final.'
            )
        return cleaned


# ---------------------------------------------------------------------------
# AudioProprioForm
# ---------------------------------------------------------------------------
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}


class AudioProprioForm(forms.ModelForm):
    class Meta:
        model = AudioProprio
        exclude = ['musica']
        widgets = {
            'nome': _tw(forms.TextInput, placeholder='Ex: Ensaio 12/03'),
            'arquivo': _tw(
                forms.ClearableFileInput,
                css=FILE_CSS,
                accept='.mp3,.wav,.ogg,.m4a,.flac',
            ),
            'tipo': _tw(forms.Select, css=SELECT_CSS),
            'duracao_segundos': _tw(forms.NumberInput, placeholder='Segundos'),
            'formato': _tw(forms.TextInput, placeholder='mp3'),
            'observacoes': _tw(forms.Textarea, css=TEXTAREA_CSS, rows='3'),
        }

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            ext = arquivo.name.rsplit('.', 1)[-1].lower() if '.' in arquivo.name else ''
            if ext not in ALLOWED_AUDIO_EXTENSIONS:
                raise forms.ValidationError(
                    f'Formatos permitidos: {", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))}.'
                )
            # Limit 200 MB
            if arquivo.size > 200 * 1024 * 1024:
                raise forms.ValidationError(
                    'O arquivo de audio nao pode exceder 200 MB.'
                )
        return arquivo


# ---------------------------------------------------------------------------
# LinkExternoForm
# ---------------------------------------------------------------------------
PROVIDER_DOMAIN_MAP = {
    'youtube': ['youtube.com', 'youtu.be', 'music.youtube.com'],
    'spotify': ['spotify.com', 'open.spotify.com'],
    'soundcloud': ['soundcloud.com'],
    'deezer': ['deezer.com'],
    'apple_music': ['music.apple.com'],
    'cifraclub': ['cifraclub.com.br'],
    'musescore': ['musescore.com'],
    'tidal': ['tidal.com'],
}


def _detect_provider(url: str) -> str:
    """Return provider key based on URL domain, or 'generico'."""
    try:
        domain = urlparse(url).netloc.lower().lstrip('www.')
    except Exception:
        return 'generico'

    for provider, domains in PROVIDER_DOMAIN_MAP.items():
        for d in domains:
            if domain == d or domain.endswith('.' + d):
                return provider
    return 'generico'


class LinkExternoForm(forms.ModelForm):
    class Meta:
        model = LinkExterno
        exclude = ['musica']
        widgets = {
            'provider': _tw(forms.Select, css=SELECT_CSS),
            'tipo_conteudo': _tw(forms.Select, css=SELECT_CSS),
            'titulo_externo': _tw(
                forms.TextInput, placeholder='Titulo do conteudo externo'
            ),
            'url': _tw(forms.URLInput, placeholder='https://...'),
            'embed_url': _tw(forms.URLInput, placeholder='URL de embed (opcional)'),
            'external_id': _tw(forms.TextInput, placeholder='ID externo (opcional)'),
            'thumbnail_url': _tw(forms.URLInput, placeholder='URL da thumbnail (opcional)'),
            'observacoes': _tw(forms.Textarea, css=TEXTAREA_CSS, rows='3'),
        }

    def clean(self):
        cleaned = super().clean()
        url = cleaned.get('url', '')
        provider = cleaned.get('provider', 'generico')

        # Auto-detect provider if left as generic
        if url and provider == 'generico':
            detected = _detect_provider(url)
            if detected != 'generico':
                cleaned['provider'] = detected

        return cleaned


# ---------------------------------------------------------------------------
# CifraForm
# ---------------------------------------------------------------------------
class CifraForm(forms.ModelForm):
    class Meta:
        model = Cifra
        exclude = ['musica']
        widgets = {
            'tipo_cifra': _tw(forms.Select, css=SELECT_CSS),
            'conteudo_texto': _tw(
                forms.Textarea,
                css=TEXTAREA_CSS,
                rows='12',
                placeholder='Cole a cifra aqui...',
            ),
            'arquivo_pdf': _tw(forms.ClearableFileInput, css=FILE_CSS, accept='.pdf'),
            'link_referencia': _tw(
                forms.URLInput, placeholder='https://cifraclub.com.br/...'
            ),
            'tom': _tw(forms.Select, css=SELECT_CSS),
            'observacoes': _tw(forms.Textarea, css=TEXTAREA_CSS, rows='3'),
        }
        help_texts = {
            'tipo_cifra': (
                'Texto: cole a cifra diretamente. '
                'PDF: envie um arquivo PDF. '
                'Link: informe a URL de referencia.'
            ),
            'conteudo_texto': 'Usado quando o tipo e "texto".',
            'arquivo_pdf': 'Usado quando o tipo e "pdf".',
            'link_referencia': 'Usado quando o tipo e "link".',
        }

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_cifra', 'texto')

        if tipo == 'texto' and not cleaned.get('conteudo_texto'):
            raise forms.ValidationError(
                'Para tipo "texto", o conteudo da cifra e obrigatorio.'
            )
        if tipo == 'pdf' and not cleaned.get('arquivo_pdf') and not self.instance.pk:
            raise forms.ValidationError(
                'Para tipo "pdf", o arquivo PDF e obrigatorio.'
            )
        if tipo == 'link' and not cleaned.get('link_referencia'):
            raise forms.ValidationError(
                'Para tipo "link", a URL de referencia e obrigatoria.'
            )

        return cleaned
