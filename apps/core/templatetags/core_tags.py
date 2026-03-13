from django import template
from django.urls import resolve, Resolver404

from apps.core.choices import TOM_CHOICES

register = template.Library()

# Build a lookup dict for tone display names
_TOM_DISPLAY_MAP = dict(TOM_CHOICES)


@register.filter(name='get_tom_display')
def get_tom_display(tom_code):
    """
    Returns the display name for a musical tone code.

    Usage in templates:
        {{ musica.tom|get_tom_display }}
        'C' -> 'C (Dó Maior)'
        'Am' -> 'Am (Lá Menor)'
    """
    if not tom_code:
        return ''
    return _TOM_DISPLAY_MAP.get(tom_code, tom_code)


@register.simple_tag(takes_context=True)
def active_nav(context, url_name, css_class='active'):
    """
    Returns the CSS class if the current URL matches the given URL name.

    Usage in templates:
        {% load core_tags %}
        <li class="{% active_nav 'core:dashboard' %}">Dashboard</li>
        <li class="{% active_nav 'musicas:musica_list' 'selected' %}">Músicas</li>
    """
    request = context.get('request')
    if not request:
        return ''

    try:
        current = resolve(request.path_info)
        # Match by url name (with or without namespace)
        current_url_name = (
            f"{current.namespace}:{current.url_name}"
            if current.namespace
            else current.url_name
        )
        if current_url_name == url_name:
            return css_class
        # Also match without namespace for convenience
        if current.url_name == url_name:
            return css_class
    except Resolver404:
        pass

    return ''


@register.filter(name='pluralize_pt')
def pluralize_pt(count, arg='s'):
    """
    Portuguese-aware pluralization filter.

    Usage:
        {{ total_musicas }} música{{ total_musicas|pluralize_pt }}
        {{ total_audios }} áudio{{ total_audios|pluralize_pt }}

    For irregular plurals, pass singular,plural suffix:
        {{ count }} canção{{ count|pluralize_pt:'ão,ões' }}
    """
    try:
        count = int(count)
    except (ValueError, TypeError):
        return ''

    if ',' in arg:
        singular, plural = arg.split(',', 1)
    else:
        singular = ''
        plural = arg

    if count == 1:
        return singular
    return plural


@register.filter(name='truncate_middle')
def truncate_middle(value, length=30):
    """
    Truncates a string in the middle, keeping start and end visible.

    Useful for file names and long paths:
        {{ arquivo.nome|truncate_middle:40 }}
        'meu_arquivo_muito_longo_nome.pdf' -> 'meu_arquivo_m...o_nome.pdf'
    """
    value = str(value)
    length = int(length)
    if len(value) <= length:
        return value
    half = (length - 3) // 2
    return f"{value[:half]}...{value[-half:]}"
