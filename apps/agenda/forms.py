from django import forms
from .models import Celebracao, TempoLiturgico

TAILWIND_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
TAILWIND_SELECT = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
TAILWIND_TEXTAREA = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y'


class CelebracaoForm(forms.ModelForm):
    class Meta:
        model = Celebracao
        fields = [
            'titulo', 'data', 'horario', 'tipo_celebracao',
            'tempo_liturgico', 'local', 'celebrante', 'repertorio', 'observacoes',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Título da celebração'}),
            'data': forms.DateInput(attrs={'class': TAILWIND_INPUT, 'type': 'date'}),
            'horario': forms.TimeInput(attrs={'class': TAILWIND_INPUT, 'type': 'time'}),
            'tipo_celebracao': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'tempo_liturgico': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'local': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Local'}),
            'celebrante': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Celebrante'}),
            'repertorio': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'observacoes': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3}),
        }


class CelebracaoFiltroForm(forms.Form):
    mes = forms.IntegerField(required=False, min_value=1, max_value=12, widget=forms.HiddenInput())
    ano = forms.IntegerField(required=False, min_value=2020, max_value=2100, widget=forms.HiddenInput())
    tipo_celebracao = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.core.choices import TIPO_CELEBRACAO_CHOICES
        self.fields['tipo_celebracao'].choices = [('', 'Todos os tipos')] + list(TIPO_CELEBRACAO_CHOICES)


class TempoLiturgicoForm(forms.ModelForm):
    class Meta:
        model = TempoLiturgico
        fields = ['nome', 'tipo', 'cor_liturgica', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'tipo': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'cor_liturgica': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Ex: verde, roxo, branco'}),
            'descricao': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA, 'rows': 3}),
        }
