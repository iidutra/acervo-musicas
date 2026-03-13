import io
import json
import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.importacao_exportacao.models import ImportacaoLote
from apps.importacao_exportacao.services import ImportService, ExportService
from apps.musicas.models import Musica, CategoriaLiturgica
from apps.repertorios.services import RecomendacaoService
from tests.factories import (
    MusicaFactory, CategoriaLiturgicaFactory, TagFactory,
    RepertorioFactory, RepertorioMusicaFactory,
)


@pytest.mark.django_db
class TestImportServiceCSV:
    def _make_csv(self, rows):
        df = pd.DataFrame(rows)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer

    def test_import_csv_basic(self):
        csv_file = self._make_csv([
            {'titulo': 'Música 1', 'tom_principal': 'C'},
            {'titulo': 'Música 2', 'tom_principal': 'Am'},
        ])
        lote = ImportacaoLote.objects.create(
            tipo_importacao='csv',
            nome_arquivo='test.csv',
            arquivo=SimpleUploadedFile('test.csv', b''),
        )
        service = ImportService()
        result = service.importar_csv(csv_file, lote)
        assert result.total_sucesso == 2
        assert result.total_erro == 0
        assert result.status == 'concluido'
        assert Musica.objects.count() == 2

    def test_import_csv_with_categorias(self):
        csv_file = self._make_csv([
            {'titulo': 'Santo', 'tom_principal': 'G', 'categorias': 'santo,comunhão'},
        ])
        lote = ImportacaoLote.objects.create(
            tipo_importacao='csv', nome_arquivo='t.csv',
            arquivo=SimpleUploadedFile('t.csv', b''),
        )
        service = ImportService()
        service.importar_csv(csv_file, lote)
        musica = Musica.objects.first()
        assert musica.categorias.count() == 2

    def test_import_csv_missing_titulo(self):
        csv_file = self._make_csv([
            {'tom_principal': 'C'},
        ])
        lote = ImportacaoLote.objects.create(
            tipo_importacao='csv', nome_arquivo='t.csv',
            arquivo=SimpleUploadedFile('t.csv', b''),
        )
        service = ImportService()
        result = service.importar_csv(csv_file, lote)
        assert result.status == 'erro'

    def test_import_csv_invalid_row(self):
        csv_file = self._make_csv([
            {'titulo': '', 'tom_principal': 'C'},
            {'titulo': 'OK', 'tom_principal': 'G'},
        ])
        lote = ImportacaoLote.objects.create(
            tipo_importacao='csv', nome_arquivo='t.csv',
            arquivo=SimpleUploadedFile('t.csv', b''),
        )
        service = ImportService()
        result = service.importar_csv(csv_file, lote)
        assert result.total_sucesso == 1
        assert result.total_erro == 1


@pytest.mark.django_db
class TestImportServiceJSON:
    def test_import_json(self):
        data = [
            {'titulo': 'JSON 1', 'tom_principal': 'D', 'categorias': ['entrada']},
            {'titulo': 'JSON 2', 'tom_principal': 'Am', 'tags': ['retiro']},
        ]
        json_file = io.BytesIO(json.dumps(data).encode('utf-8'))
        lote = ImportacaoLote.objects.create(
            tipo_importacao='json', nome_arquivo='t.json',
            arquivo=SimpleUploadedFile('t.json', b''),
        )
        service = ImportService()
        result = service.importar_json(json_file, lote)
        assert result.total_sucesso == 2
        assert Musica.objects.count() == 2


@pytest.mark.django_db
class TestExportService:
    def test_export_csv(self):
        MusicaFactory.create_batch(3)
        service = ExportService()
        response = service.exportar_csv(Musica.objects.all())
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self):
        MusicaFactory.create_batch(2)
        service = ExportService()
        response = service.exportar_excel(Musica.objects.all())
        assert response.status_code == 200
        assert 'spreadsheetml' in response['Content-Type']

    def test_export_json(self):
        MusicaFactory.create_batch(2)
        service = ExportService()
        response = service.exportar_json(Musica.objects.all())
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) == 2

    def test_export_zip(self):
        MusicaFactory.create_batch(2)
        service = ExportService()
        response = service.exportar_zip(Musica.objects.all())
        assert response.status_code == 200
        assert 'application/zip' in response['Content-Type']


@pytest.mark.django_db
class TestRecomendacaoService:
    def test_recomendar_vazio(self):
        service = RecomendacaoService()
        resultado = service.recomendar_repertorio_completo()
        assert isinstance(resultado, dict)
        for momento, sugestoes in resultado.items():
            assert isinstance(sugestoes, list)

    def test_recomendar_com_dados(self):
        cat_entrada = CategoriaLiturgicaFactory(nome='entrada')
        cat_comunhao = CategoriaLiturgicaFactory(nome='comunhão')
        MusicaFactory.create_batch(3, categorias=[cat_entrada])
        MusicaFactory.create_batch(2, categorias=[cat_comunhao])

        service = RecomendacaoService()
        resultado = service.recomendar_repertorio_completo()
        assert len(resultado['entrada']) > 0
        assert len(resultado['comunhão']) > 0

    def test_penalidade_uso_recente(self):
        cat = CategoriaLiturgicaFactory(nome='entrada')
        musica_usada = MusicaFactory(categorias=[cat])
        musica_nova = MusicaFactory(categorias=[cat])

        rep = RepertorioFactory()
        RepertorioMusicaFactory(repertorio=rep, musica=musica_usada)

        service = RecomendacaoService(dias_recencia=90)
        resultado = service.recomendar_por_momento('entrada')

        scores = {s['musica'].pk: s['score'] for s in resultado}
        if musica_usada.pk in scores and musica_nova.pk in scores:
            assert scores[musica_nova.pk] >= scores[musica_usada.pk]
