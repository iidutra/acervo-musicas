import pytest
from apps.core.utils import normalizar_tom


class TestNormalizarTom:
    """Testes para normalização de tons musicais."""

    @pytest.mark.parametrize('input_tom,expected', [
        ('C', 'C'),
        ('Am', 'Am'),
        ('F#m', 'F#m'),
        ('Bb', 'Bb'),
        ('Eb', 'Eb'),
        ('G', 'G'),
    ])
    def test_tons_validos_diretos(self, input_tom, expected):
        assert normalizar_tom(input_tom) == expected

    @pytest.mark.parametrize('input_tom,expected', [
        ('Dó', 'C'),
        ('Ré', 'D'),
        ('Mi', 'E'),
        ('Fá', 'F'),
        ('Sol', 'G'),
        ('Lá', 'A'),
        ('Si', 'B'),
    ])
    def test_tons_portugues_maior(self, input_tom, expected):
        assert normalizar_tom(input_tom) == expected

    @pytest.mark.parametrize('input_tom,expected', [
        ('Lá menor', 'Am'),
        ('Ré menor', 'Dm'),
        ('Mi menor', 'Em'),
    ])
    def test_tons_portugues_menor(self, input_tom, expected):
        assert normalizar_tom(input_tom) == expected

    @pytest.mark.parametrize('input_tom,expected', [
        ('Si bemol', 'Bb'),
        ('Fá sustenido menor', 'F#m'),
        ('Sol sustenido menor', 'G#m'),
    ])
    def test_tons_portugues_alterados(self, input_tom, expected):
        assert normalizar_tom(input_tom) == expected

    def test_tom_vazio(self):
        assert normalizar_tom('') is None
        assert normalizar_tom(None) is None
        assert normalizar_tom('   ') is None

    def test_tom_irreconhecivel(self):
        assert normalizar_tom('xyz') is None
        assert normalizar_tom('123') is None
