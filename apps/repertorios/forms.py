from django import forms
from django.forms import inlineformset_factory

from apps.repertorios.models import Repertorio, RepertorioMusica


# ---------------------------------------------------------------------------
# Tailwind CSS helper classes
# ---------------------------------------------------------------------------

_tw_input = (
    'block w-full rounded-md border-gray-300 shadow-sm '
    'focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
)

_tw_select = (
    'block w-full rounded-md border-gray-300 shadow-sm '
    'focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
)

_tw_textarea = (
    'block w-full rounded-md border-gray-300 shadow-sm '
    'focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
)

_tw_checkbox = (
    'rounded border-gray-300 text-indigo-600 shadow-sm '
    'focus:ring-indigo-500'
)


# ---------------------------------------------------------------------------
# RepertorioForm
# ---------------------------------------------------------------------------

class RepertorioForm(forms.ModelForm):
    class Meta:
        model = Repertorio
        fields = ['nome', 'data_celebracao', 'tipo_celebracao', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': _tw_input,
                'placeholder': 'Nome do repertório',
            }),
            'data_celebracao': forms.DateInput(attrs={
                'class': _tw_input,
                'type': 'date',
            }),
            'tipo_celebracao': forms.Select(attrs={
                'class': _tw_select,
            }),
            'observacoes': forms.Textarea(attrs={
                'class': _tw_textarea,
                'rows': 3,
                'placeholder': 'Observações gerais sobre o repertório...',
            }),
        }


# ---------------------------------------------------------------------------
# RepertorioMusicaForm
# ---------------------------------------------------------------------------

class RepertorioMusicaForm(forms.ModelForm):
    class Meta:
        model = RepertorioMusica
        fields = [
            'musica',
            'ordem',
            'categoria_no_repertorio',
            'tom_no_repertorio',
            'observacoes',
        ]
        widgets = {
            'musica': forms.Select(attrs={
                'class': f'{_tw_select} js-select-search',
                'data-placeholder': 'Selecione uma música...',
            }),
            'ordem': forms.NumberInput(attrs={
                'class': _tw_input,
                'min': '0',
                'style': 'width: 5rem;',
            }),
            'categoria_no_repertorio': forms.Select(attrs={
                'class': _tw_select,
            }),
            'tom_no_repertorio': forms.Select(attrs={
                'class': _tw_select,
            }),
            'observacoes': forms.Textarea(attrs={
                'class': _tw_textarea,
                'rows': 2,
                'placeholder': 'Observações...',
            }),
        }


# ---------------------------------------------------------------------------
# Inline formset: RepertorioMusica linked to Repertorio
# ---------------------------------------------------------------------------

RepertorioMusicaFormSet = inlineformset_factory(
    Repertorio,
    RepertorioMusica,
    form=RepertorioMusicaForm,
    extra=3,
    can_delete=True,
)
