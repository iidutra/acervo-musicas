from django import forms
from apps.core.choices import TIPO_IMPORTACAO_CHOICES


FORMATO_EXPORTACAO_CHOICES = [
    ('csv', 'CSV'),
    ('excel', 'Excel (.xlsx)'),
    ('json', 'JSON'),
    ('zip', 'ZIP (completo)'),
]

FILTRO_ATIVO_CHOICES = [
    ('todos', 'Todos'),
    ('ativos', 'Apenas Ativos'),
    ('inativos', 'Apenas Inativos'),
]

EXTENSOES_POR_TIPO = {
    'csv': ['.csv'],
    'excel': ['.xlsx', '.xls'],
    'json': ['.json'],
    'zip': ['.zip'],
}

tw_input = (
    'block w-full rounded-md border-gray-300 shadow-sm '
    'focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
)

tw_select = (
    'block w-full rounded-md border-gray-300 shadow-sm '
    'focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
)

tw_checkbox = 'rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'


class ImportacaoForm(forms.Form):
    """Formulário para importação de músicas."""

    tipo_importacao = forms.ChoiceField(
        choices=TIPO_IMPORTACAO_CHOICES,
        label='Tipo de Arquivo',
        widget=forms.Select(attrs={'class': tw_select}),
    )
    arquivo = forms.FileField(
        label='Arquivo',
        widget=forms.ClearableFileInput(attrs={'class': tw_input, 'accept': '.csv,.xlsx,.xls,.json,.zip'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_importacao')
        arquivo = cleaned_data.get('arquivo')

        if tipo and arquivo:
            extensoes_validas = EXTENSOES_POR_TIPO.get(tipo, [])
            nome = arquivo.name.lower()
            if not any(nome.endswith(ext) for ext in extensoes_validas):
                extensoes_str = ', '.join(extensoes_validas)
                raise forms.ValidationError(
                    f'Extensão do arquivo incompatível com o tipo selecionado. '
                    f'Esperado: {extensoes_str}'
                )

        return cleaned_data


class ExportacaoForm(forms.Form):
    """Formulário para exportação de músicas."""

    formato = forms.ChoiceField(
        choices=FORMATO_EXPORTACAO_CHOICES,
        label='Formato de Exportação',
        widget=forms.Select(attrs={'class': tw_select}),
    )
    incluir_midias = forms.BooleanField(
        required=False,
        initial=False,
        label='Incluir mídias (PDFs, áudios, cifras)',
        help_text='Disponível apenas para exportação ZIP.',
        widget=forms.CheckboxInput(attrs={'class': tw_checkbox}),
    )
    filtro_ativo = forms.ChoiceField(
        choices=FILTRO_ATIVO_CHOICES,
        label='Filtrar por Status',
        initial='todos',
        widget=forms.Select(attrs={'class': tw_select}),
    )
