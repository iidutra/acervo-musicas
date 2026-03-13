import pytest
from unittest.mock import patch, MagicMock

from apps.integracoes.services import (
    YouTubeService, SpotifyService, detect_provider,
    fetch_link_metadata, enrich_link,
)


class TestDetectProvider:
    def test_youtube(self):
        assert detect_provider('https://www.youtube.com/watch?v=abc') == 'youtube'
        assert detect_provider('https://youtu.be/abc') == 'youtube'

    def test_spotify(self):
        assert detect_provider('https://open.spotify.com/track/abc') == 'spotify'

    def test_apple_music(self):
        assert detect_provider('https://music.apple.com/br/album/abc') == 'apple_music'

    def test_generic(self):
        assert detect_provider('https://example.com/page') == 'generico'


class TestYouTubeService:
    def test_extract_video_id(self):
        assert YouTubeService.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        assert YouTubeService.extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        assert YouTubeService.extract_video_id('https://example.com') is None

    @patch('apps.integracoes.services.requests.get')
    def test_fetch_metadata_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'title': 'Test Video',
            'thumbnail_url': 'https://img.youtube.com/thumb.jpg',
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = YouTubeService.fetch_metadata('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        assert result is not None
        assert result['titulo_externo'] == 'Test Video'
        assert result['provider'] == 'youtube'
        assert 'embed' in result['embed_url']

    @patch('apps.integracoes.services.requests.get')
    def test_fetch_metadata_failure(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        result = YouTubeService.fetch_metadata('https://www.youtube.com/watch?v=abc')
        assert result is None


class TestSpotifyService:
    def test_extract_spotify_id(self):
        result = SpotifyService.extract_spotify_id('https://open.spotify.com/track/abc123')
        assert result == ('track', 'abc123')

    def test_extract_spotify_id_invalid(self):
        assert SpotifyService.extract_spotify_id('https://example.com') is None


@pytest.mark.django_db
class TestEnrichLink:
    @patch('apps.integracoes.services.fetch_link_metadata')
    def test_enrich_fills_empty_fields(self, mock_fetch):
        from tests.factories import LinkExternoFactory
        mock_fetch.return_value = {
            'titulo_externo': 'Enriched Title',
            'thumbnail_url': 'https://example.com/thumb.jpg',
            'embed_url': 'https://youtube.com/embed/abc',
            'provider': 'youtube',
        }
        link = LinkExternoFactory(titulo_externo='', thumbnail_url='')
        result = enrich_link(link)
        assert result is True
        link.refresh_from_db()
        assert link.titulo_externo == 'Enriched Title'

    @patch('apps.integracoes.services.fetch_link_metadata')
    def test_enrich_no_overwrite(self, mock_fetch):
        from tests.factories import LinkExternoFactory
        mock_fetch.return_value = {
            'titulo_externo': 'New Title',
            'provider': 'youtube',
        }
        link = LinkExternoFactory(titulo_externo='Original Title')
        result = enrich_link(link)
        link.refresh_from_db()
        assert link.titulo_externo == 'Original Title'
