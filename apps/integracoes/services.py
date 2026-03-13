"""
Serviços de integração com plataformas externas.

Regras fundamentais:
- NÃO baixar conteúdo externo (vídeos, músicas, arquivos)
- Apenas buscar metadados (título, thumbnail, duração, embed URL)
- Tratar erros graciosamente
"""
import logging
import re
from urllib.parse import urlencode, urlparse, parse_qs

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 10  # seconds


class YouTubeService:
    """Busca metadados de vídeos do YouTube via oEmbed (sem API key)."""

    OEMBED_URL = 'https://www.youtube.com/oembed'

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        """Extrai o video ID de uma URL do YouTube."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @classmethod
    def fetch_metadata(cls, url: str) -> dict | None:
        """Busca metadados de um vídeo do YouTube."""
        video_id = cls.extract_video_id(url)
        if not video_id:
            return None

        try:
            params = {'url': url, 'format': 'json'}
            response = requests.get(
                cls.OEMBED_URL,
                params=params,
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            return {
                'external_id': video_id,
                'titulo_externo': data.get('title', ''),
                'thumbnail_url': data.get('thumbnail_url', ''),
                'embed_url': f'https://www.youtube.com/embed/{video_id}',
                'provider': 'youtube',
            }
        except Exception as e:
            logger.warning('Erro ao buscar metadados do YouTube para %s: %s', url, e)
            return None


class SpotifyService:
    """Busca metadados do Spotify via oEmbed (sem API key)."""

    OEMBED_URL = 'https://open.spotify.com/oembed'

    @staticmethod
    def extract_spotify_id(url: str) -> tuple[str, str] | None:
        """Extrai tipo e ID de uma URL do Spotify. Returns (type, id) or None."""
        match = re.search(
            r'open\.spotify\.com/(track|album|playlist|artist)/([a-zA-Z0-9]+)',
            url,
        )
        if match:
            return match.group(1), match.group(2)
        return None

    @classmethod
    def fetch_metadata(cls, url: str) -> dict | None:
        """Busca metadados do Spotify."""
        result = cls.extract_spotify_id(url)
        if not result:
            return None

        spotify_type, spotify_id = result

        try:
            response = requests.get(
                cls.OEMBED_URL,
                params={'url': url},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            return {
                'external_id': spotify_id,
                'titulo_externo': data.get('title', ''),
                'thumbnail_url': data.get('thumbnail_url', ''),
                'embed_url': f'https://open.spotify.com/embed/{spotify_type}/{spotify_id}',
                'provider': 'spotify',
            }
        except Exception as e:
            logger.warning('Erro ao buscar metadados do Spotify para %s: %s', url, e)
            return None


class GenericOEmbedService:
    """Tenta buscar metadados via oEmbed genérico."""

    @staticmethod
    def fetch_metadata(url: str) -> dict | None:
        """Tenta oEmbed discovery para URLs genéricas."""
        try:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            # Try to extract title from HTML
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ''

            return {
                'titulo_externo': title,
                'provider': 'generico',
            } if title else None
        except Exception as e:
            logger.debug('Erro ao buscar metadados genéricos para %s: %s', url, e)
            return None


def detect_provider(url: str) -> str:
    """Detecta o provider a partir da URL."""
    domain = urlparse(url).netloc.lower()
    if 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    if 'spotify.com' in domain:
        return 'spotify'
    if 'music.apple.com' in domain:
        return 'apple_music'
    return 'generico'


def fetch_link_metadata(url: str) -> dict | None:
    """
    Busca metadados para uma URL, detectando automaticamente o provider.
    Retorna dict com campos para atualizar no LinkExterno ou None.
    """
    provider = detect_provider(url)

    if provider == 'youtube':
        return YouTubeService.fetch_metadata(url)
    elif provider == 'spotify':
        return SpotifyService.fetch_metadata(url)
    else:
        return GenericOEmbedService.fetch_metadata(url)


def enrich_link(link) -> bool:
    """
    Enriquece um objeto LinkExterno com metadados da URL.
    Retorna True se houve atualização.
    """
    metadata = fetch_link_metadata(link.url)
    if not metadata:
        return False

    updated = False
    for field, value in metadata.items():
        if value and hasattr(link, field):
            current = getattr(link, field)
            if not current:  # Only fill empty fields
                setattr(link, field, value)
                updated = True

    if updated:
        update_fields = [f for f in metadata if hasattr(link, f) and metadata[f]]
        link.save(update_fields=update_fields)

    return updated
