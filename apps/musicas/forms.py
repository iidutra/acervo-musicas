from django import forms
from apps.core.choices import TOM_CHOICES
from .models import Musica, CategoriaLiturgica, Tag


TAILWIND_INPUT = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
TAILWIND_TEXTAREA = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y'
TAILWIND_SELECT = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white'
TAILWIND_CHECKBOX = 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'


class MusicaForm(forms.ModelForm):
    class Meta:
        model = Musica
        fields = [
            'titulo',
            'subtitulo',
            'letra',
            'tom_principal',
            'andamento',
            'compasso',
            'observacoes',
            'origem',
            'ativo',
            'categorias',
            'tags',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Título da música',
            }),
            'subtitulo': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Subtítulo (opcional)',
            }),
            'letra': forms.Textarea(attrs={
                'class': TAILWIND_TEXTAREA,
                'rows': 12,
                'placeholder': 'Cole aqui a letra completa da música...',
            }),
            'tom_principal': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
            'andamento': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Ex: Moderado, Rápido, Lento',
            }),
            'compasso': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Ex: 4/4, 3/4, 6/8',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': TAILWIND_TEXTAREA,
                'rows': 4,
                'placeholder': 'Observações adicionais...',
            }),
            'origem': forms.Select(attrs={
                'class': TAILWIND_SELECT,
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': TAILWIND_CHECKBOX,
            }),
            'categorias': forms.CheckboxSelectMultiple(attrs={
                'class': TAILWIND_CHECKBOX,
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': TAILWIND_CHECKBOX,
            }),
        }


class CategoriaLiturgicaForm(forms.ModelForm):
    class Meta:
        model = CategoriaLiturgica
        fields = ['nome', 'descricao', 'ordem', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Nome da categoria',
            }),
            'descricao': forms.Textarea(attrs={
                'class': TAILWIND_TEXTAREA,
                'rows': 3,
                'placeholder': 'Descrição da categoria (opcional)',
            }),
            'ordem': forms.NumberInput(attrs={
                'class': TAILWIND_INPUT,
                'min': 0,
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': TAILWIND_CHECKBOX,
            }),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'Nome da tag',
            }),
        }


class MusicaFiltroForm(forms.Form):
    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Buscar por título, subtítulo ou letra...',
        }),
    )
    tom = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tons')] + list(TOM_CHOICES),
        widget=forms.Select(attrs={
            'class': TAILWIND_SELECT,
        }),
    )
    categoria = forms.ModelChoiceField(
        required=False,
        queryset=CategoriaLiturgica.objects.filter(ativo=True),
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={
            'class': TAILWIND_SELECT,
        }),
    )
    tag = forms.ModelChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        empty_label='Todas as tags',
        widget=forms.Select(attrs={
            'class': TAILWIND_SELECT,
        }),
    )
    tem_pdf = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': TAILWIND_CHECKBOX,
        }),
    )
    tem_audio = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': TAILWIND_CHECKBOX,
        }),
    )
    tem_cifra = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': TAILWIND_CHECKBOX,
        }),
    )
    ativo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('ativo', 'Somente ativos'),
            ('inativo', 'Somente inativos'),
        ],
        widget=forms.Select(attrs={
            'class': TAILWIND_SELECT,
        }),
    )
