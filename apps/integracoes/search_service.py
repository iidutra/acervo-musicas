"""
Serviço de pesquisa de músicas.
Busca vídeos no YouTube, letras e cifras em fontes públicas.

Estratégia de busca:
- YouTube: scraping da página de resultados (ytInitialData)
- Letras: Genius API para encontrar artista/título, depois tenta Letras.mus.br
  por slug, com fallback para Genius lyrics
- Cifras: Genius API para artista/título, depois CifraClub por slug
"""
import logging
import re
from unicodedata import normalize

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TIMEOUT = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
}


def _slugify(text: str) -> str:
    """Converte texto para slug (ex: 'Gabriela Rocha' -> 'gabriela-rocha')."""
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text


def _genius_search(query: str) -> list[dict]:
    """Busca músicas via Genius API (não requer autenticação)."""
    try:
        r = requests.get(
            'https://genius.com/api/search/song',
            params={'q': query},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        sections = data.get('response', {}).get('sections', [])
        if not sections:
            return []
        hits = sections[0].get('hits', [])
        results = []
        for hit in hits:
            song = hit.get('result', {})
            results.append({
                'title': song.get('title', ''),
                'artist': song.get('artist_names', ''),
                'genius_url': song.get('url', ''),
            })
        return results
    except Exception as e:
        logger.warning('Genius search falhou: %s', e)
        return []


# ---- YouTube ----

def buscar_youtube(query: str, limit: int = 6) -> list[dict]:
    """Busca vídeos no YouTube via scraping da página de resultados."""
    import json as _json

    try:
        search_url = 'https://www.youtube.com/results'
        params = {'search_query': query}

        response = requests.get(
            search_url, params=params, headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()

        # YouTube embeds JSON data in the page as ytInitialData
        match = re.search(r'var ytInitialData = ({.*?});', response.text)
        if not match:
            match = re.search(r'ytInitialData\s*=\s*({.*?});', response.text)
        if not match:
            logger.warning('YouTube: não encontrou ytInitialData na página')
            return []

        data = _json.loads(match.group(1))

        videos = []
        try:
            contents = (
                data['contents']['twoColumnSearchResultsRenderer']
                ['primaryContents']['sectionListRenderer']['contents']
            )
        except (KeyError, TypeError):
            return []

        for section in contents:
            items = (
                section.get('itemSectionRenderer', {})
                .get('contents', [])
            )
            for item in items:
                renderer = item.get('videoRenderer')
                if not renderer:
                    continue

                video_id = renderer.get('videoId', '')
                if not video_id:
                    continue

                title_runs = renderer.get('title', {}).get('runs', [])
                titulo = title_runs[0]['text'] if title_runs else ''

                canal_runs = renderer.get('ownerText', {}).get('runs', [])
                canal = canal_runs[0]['text'] if canal_runs else ''

                duracao = (
                    renderer.get('lengthText', {})
                    .get('simpleText', '')
                )

                view_text = (
                    renderer.get('viewCountText', {})
                    .get('simpleText', '')
                )

                thumbnail = ''
                thumbs = renderer.get('thumbnail', {}).get('thumbnails', [])
                if thumbs:
                    thumbnail = thumbs[-1].get('url', '')

                videos.append({
                    'video_id': video_id,
                    'titulo': titulo,
                    'canal': canal,
                    'duracao': duracao,
                    'thumbnail': thumbnail,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'views': view_text,
                })

                if len(videos) >= limit:
                    break

            if len(videos) >= limit:
                break

        return videos

    except Exception as e:
        logger.error('Erro ao buscar no YouTube: %s', e)
        return []


# ---- Letra ----

def buscar_letra(query: str) -> dict | None:
    """
    Busca letra de música.
    Usa Genius para encontrar artista/título, tenta Letras.mus.br por slug,
    com fallback para scraping do Genius.
    """
    genius_results = _genius_search(query)
    if not genius_results:
        return None

    song = genius_results[0]
    artist_slug = _slugify(song['artist'])
    title_slug = _slugify(song['title'])

    # Tentar Letras.mus.br por slug
    try:
        result = _scrape_letras_mus_br(artist_slug, title_slug)
        if result:
            return result
    except Exception as e:
        logger.debug('Letras.mus.br falhou para %s/%s: %s', artist_slug, title_slug, e)

    # Fallback: scrape Genius
    try:
        return _scrape_genius_lyrics(song)
    except Exception as e:
        logger.warning('Genius lyrics falhou: %s', e)

    return None


def _scrape_letras_mus_br(artist_slug: str, title_slug: str) -> dict | None:
    """Busca letra no Letras.mus.br usando slugs do artista/título."""
    song_url = f'https://www.letras.mus.br/{artist_slug}/{title_slug}/'

    response = requests.get(song_url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code == 404:
        return None
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract lyrics
    lyrics_div = soup.select_one('.lyric-original')
    if not lyrics_div:
        lyrics_div = soup.select_one('[data-lyrics-original]')
    if not lyrics_div:
        lyrics_div = soup.select_one('.cnt-letra')

    if not lyrics_div:
        return None

    # Extract text preserving line breaks
    for br in lyrics_div.find_all('br'):
        br.replace_with('\n')
    for p in lyrics_div.find_all('p'):
        p.insert_after('\n\n')

    letra = lyrics_div.get_text().strip()
    letra = re.sub(r'\n{3,}', '\n\n', letra)

    # Extract title and artist
    titulo_el = soup.select_one('h1.cnt-head_title')
    if not titulo_el:
        titulo_el = soup.select_one('h1')
    titulo = titulo_el.get_text().strip() if titulo_el else ''

    artista_el = soup.select_one('.cnt-head_subtitle a')
    if not artista_el:
        artista_el = soup.select_one('h2.cnt-head_subtitle')
    artista = artista_el.get_text().strip() if artista_el else ''

    return {
        'titulo': titulo,
        'artista': artista,
        'letra': letra,
        'fonte': 'Letras.mus.br',
        'url': song_url,
    }


def _scrape_genius_lyrics(song: dict) -> dict | None:
    """Scrape letra do Genius como fallback."""
    genius_url = song.get('genius_url')
    if not genius_url:
        return None

    response = requests.get(genius_url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    lyrics_divs = soup.select('div[data-lyrics-container]')
    if not lyrics_divs:
        return None

    for div in lyrics_divs:
        for br in div.find_all('br'):
            br.replace_with('\n')

    texto = '\n'.join(d.get_text() for d in lyrics_divs)
    # Remove header like "3 ContributorsSong Title Lyrics\n"
    letra = re.sub(r'^\d+\s*Contributors.*?Lyrics\n?', '', texto, count=1)
    # Remove annotations like [Verso 1], [Refrão] etc
    letra = re.sub(r'\[.*?\]\n?', '', letra).strip()
    letra = re.sub(r'\n{3,}', '\n\n', letra)

    return {
        'titulo': song['title'],
        'artista': song['artist'],
        'letra': letra,
        'fonte': 'Genius',
        'url': genius_url,
    }


# ---- Cifra ----

def buscar_cifra(query: str) -> dict | None:
    """
    Busca cifra (acordes + letra) no CifraClub.
    Usa Genius para encontrar artista/título e monta URL do CifraClub.
    """
    try:
        return _buscar_cifraclub(query)
    except Exception as e:
        logger.warning('Erro ao buscar cifra no CifraClub: %s', e)
    return None


def _buscar_cifraclub(query: str) -> dict | None:
    """Busca cifra no CifraClub.com.br usando Genius para descobrir artista/título."""
    genius_results = _genius_search(query)
    if not genius_results:
        return None

    # Tenta os primeiros resultados do Genius
    for song in genius_results[:3]:
        # Remove "feat/ft" suffixes - CifraClub usa só o artista principal
        artist_name = re.split(r'\s*[\(\[]\s*(?:feat|ft)\.?', song['artist'], flags=re.I)[0]
        artist_slug = _slugify(artist_name)
        title_slug = _slugify(song['title'])
        song_url = f'https://www.cifraclub.com.br/{artist_slug}/{title_slug}/'

        try:
            response = requests.get(
                song_url, headers=HEADERS, timeout=TIMEOUT
            )
            if response.status_code == 404:
                continue
            response.raise_for_status()
        except requests.RequestException:
            continue

        result = _parse_cifraclub_page(response.text, song_url)
        if result:
            return result

    return None


def _parse_cifraclub_page(html: str, song_url: str) -> dict | None:
    """Extrai dados de cifra de uma página do CifraClub."""
    soup = BeautifulSoup(html, 'html.parser')

    # Extract cifra content - CifraClub uses <pre> inside the cifra area
    cifra_pre = soup.select_one('div.cifra pre')
    if not cifra_pre:
        cifra_pre = soup.select_one('pre.cifra')
    if not cifra_pre:
        cifra_pre = soup.select_one('[class*="cifra"] pre')
    if not cifra_pre:
        for pre in soup.select('pre'):
            text = pre.get_text()
            if re.search(r'\b[A-G][#b]?m?\b', text) and len(text) > 50:
                cifra_pre = pre
                break

    if not cifra_pre:
        return None

    # Process the cifra text preserving chord positioning
    cifra_texto = ''
    for child in cifra_pre.children:
        if hasattr(child, 'name') and child.name == 'b':
            cifra_texto += child.get_text()
        elif hasattr(child, 'name') and child.name == 'br':
            cifra_texto += '\n'
        else:
            text = str(child) if not hasattr(child, 'get_text') else child.get_text()
            cifra_texto += text

    cifra_texto = cifra_texto.strip()
    if not cifra_texto:
        return None

    # Extract title
    titulo_el = soup.select_one('h1.t1')
    if not titulo_el:
        titulo_el = soup.select_one('h1')
    titulo = titulo_el.get_text().strip() if titulo_el else ''

    # Extract artist
    artista_el = soup.select_one('h2.t3 a')
    if not artista_el:
        artista_el = soup.select_one('h2.t3')
    artista = artista_el.get_text().strip() if artista_el else ''

    # Extract key/tom
    tom = ''
    tom_el = soup.select_one('[class*="tom"] .cifra_tom')
    if not tom_el:
        tom_el = soup.select_one('.cipher-tom')
    if tom_el:
        tom = tom_el.get_text().strip()

    return {
        'titulo': titulo,
        'artista': artista,
        'cifra_texto': cifra_texto,
        'tom': tom,
        'fonte': 'CifraClub',
        'url': song_url,
    }
