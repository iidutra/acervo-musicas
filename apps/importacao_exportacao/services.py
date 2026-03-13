import io
import json
import logging
import os
import tempfile
import zipfile
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponse

from apps.core.choices import TOM_CHOICES
from apps.core.utils import normalizar_tom
from apps.musicas.models import CategoriaLiturgica, Musica, Tag
from apps.arquivos.models import AudioProprio, Cifra, LinkExterno, PDFArquivo
from apps.importacao_exportacao.models import ImportacaoLote

logger = logging.getLogger(__name__)

VALID_TOMS = {code for code, _ in TOM_CHOICES}


class ImportService:
    """Serviço para importação de músicas em diversos formatos."""

    def importar_csv(self, arquivo, lote: ImportacaoLote) -> ImportacaoLote:
        """Importa músicas a partir de um arquivo CSV."""
        lote.status = 'processando'
        lote.save(update_fields=['status'])

        try:
            df = pd.read_csv(arquivo, encoding='utf-8-sig')
            return self._processar_dataframe(df, lote)
        except Exception as e:
            lote.status = 'erro'
            lote.log += f'\n[ERRO FATAL] Falha ao ler CSV: {e}'
            lote.save(update_fields=['status', 'log'])
            return lote

    def importar_excel(self, arquivo, lote: ImportacaoLote) -> ImportacaoLote:
        """Importa músicas a partir de um arquivo Excel."""
        lote.status = 'processando'
        lote.save(update_fields=['status'])

        try:
            df = pd.read_excel(arquivo, engine='openpyxl')
            return self._processar_dataframe(df, lote)
        except Exception as e:
            lote.status = 'erro'
            lote.log += f'\n[ERRO FATAL] Falha ao ler Excel: {e}'
            lote.save(update_fields=['status', 'log'])
            return lote

    def importar_json(self, arquivo, lote: ImportacaoLote) -> ImportacaoLote:
        """Importa músicas a partir de um arquivo JSON."""
        lote.status = 'processando'
        lote.save(update_fields=['status'])

        try:
            conteudo = arquivo.read()
            if isinstance(conteudo, bytes):
                conteudo = conteudo.decode('utf-8-sig')
            dados = json.loads(conteudo)

            if not isinstance(dados, list):
                dados = [dados]

            lote.total_registros = len(dados)
            lote.save(update_fields=['total_registros'])

            for idx, item in enumerate(dados, start=1):
                try:
                    self._criar_musica_from_dict(item, lote, idx)
                    lote.total_sucesso += 1
                except Exception as e:
                    lote.total_erro += 1
                    lote.log += f'\n[ERRO] Registro {idx}: {e}'

            lote.status = 'concluido'
            lote.save(update_fields=[
                'status', 'total_sucesso', 'total_erro', 'log',
            ])
            return lote

        except Exception as e:
            lote.status = 'erro'
            lote.log += f'\n[ERRO FATAL] Falha ao ler JSON: {e}'
            lote.save(update_fields=['status', 'log'])
            return lote

    def importar_zip(self, arquivo, lote: ImportacaoLote) -> ImportacaoLote:
        """Importa músicas a partir de um arquivo ZIP contendo CSV e mídias."""
        lote.status = 'processando'
        lote.save(update_fields=['status'])

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(arquivo, 'r') as zf:
                    zf.extractall(tmpdir)

                # Locate musicas.csv
                csv_path = os.path.join(tmpdir, 'musicas.csv')
                if not os.path.isfile(csv_path):
                    # Try looking one level deeper
                    for root, dirs, files in os.walk(tmpdir):
                        if 'musicas.csv' in files:
                            csv_path = os.path.join(root, 'musicas.csv')
                            break

                if not os.path.isfile(csv_path):
                    lote.status = 'erro'
                    lote.log += '\n[ERRO FATAL] Arquivo musicas.csv não encontrado no ZIP.'
                    lote.save(update_fields=['status', 'log'])
                    return lote

                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                lote = self._processar_dataframe(df, lote)

                # Link media files to created musicas
                base_dir = os.path.dirname(csv_path)
                self._vincular_midias_zip(base_dir, lote)

            return lote

        except Exception as e:
            lote.status = 'erro'
            lote.log += f'\n[ERRO FATAL] Falha ao processar ZIP: {e}'
            lote.save(update_fields=['status', 'log'])
            return lote

    def _processar_dataframe(self, df: pd.DataFrame, lote: ImportacaoLote) -> ImportacaoLote:
        """Lógica compartilhada para processar CSV/Excel via DataFrame."""
        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

        if 'titulo' not in df.columns:
            lote.status = 'erro'
            lote.log += '\n[ERRO FATAL] Coluna obrigatória "titulo" não encontrada.'
            lote.save(update_fields=['status', 'log'])
            return lote

        lote.total_registros = len(df)
        lote.save(update_fields=['total_registros'])

        for idx, row in df.iterrows():
            row_num = idx + 2  # header is row 1, data starts at 2
            try:
                self._criar_musica_from_row(row, lote, row_num)
                lote.total_sucesso += 1
            except Exception as e:
                lote.total_erro += 1
                lote.log += f'\n[ERRO] Linha {row_num}: {e}'

        lote.status = 'concluido'
        lote.save(update_fields=[
            'status', 'total_sucesso', 'total_erro', 'log',
        ])
        return lote

    def _criar_musica_from_row(self, row, lote: ImportacaoLote, row_num: int) -> Musica:
        """Cria uma Musica a partir de uma linha do DataFrame."""
        titulo = str(row.get('titulo', '')).strip()
        if not titulo or titulo == 'nan':
            raise ValueError(f'Título vazio na linha {row_num}.')

        tom_raw = str(row.get('tom_principal', 'NI')).strip()
        if tom_raw == 'nan' or not tom_raw:
            tom_raw = 'NI'

        tom_normalizado = normalizar_tom(tom_raw)
        if tom_normalizado and tom_normalizado in VALID_TOMS:
            tom_principal = tom_normalizado
        elif tom_raw in VALID_TOMS:
            tom_principal = tom_raw
        else:
            tom_principal = 'NI'

        subtitulo = self._safe_str(row.get('subtitulo', ''))
        letra = self._safe_str(row.get('letra', ''))
        observacoes = self._safe_str(row.get('observacoes', ''))

        with transaction.atomic():
            musica = Musica.objects.create(
                titulo=titulo,
                subtitulo=subtitulo,
                letra=letra,
                tom_principal=tom_principal,
                observacoes=observacoes,
                origem='importacao',
            )

            # Categorias (comma-separated)
            categorias_raw = self._safe_str(row.get('categorias', ''))
            if categorias_raw:
                for cat_nome in categorias_raw.split(','):
                    cat_nome = cat_nome.strip()
                    if cat_nome:
                        cat, _ = CategoriaLiturgica.objects.get_or_create(
                            nome=cat_nome,
                            defaults={'descricao': '', 'ativo': True},
                        )
                        musica.categorias.add(cat)

            # Tags (comma-separated)
            tags_raw = self._safe_str(row.get('tags', ''))
            if tags_raw:
                for tag_nome in tags_raw.split(','):
                    tag_nome = tag_nome.strip()
                    if tag_nome:
                        tag, _ = Tag.objects.get_or_create(nome=tag_nome)
                        musica.tags.add(tag)

            # Links opcionais
            link_video = self._safe_str(row.get('link_video', ''))
            if link_video:
                LinkExterno.objects.create(
                    musica=musica,
                    url=link_video,
                    tipo_conteudo='video',
                    provider='generico',
                    titulo_externo=f'Vídeo - {titulo}',
                )

            link_audio = self._safe_str(row.get('link_audio', ''))
            if link_audio:
                LinkExterno.objects.create(
                    musica=musica,
                    url=link_audio,
                    tipo_conteudo='audio',
                    provider='generico',
                    titulo_externo=f'Áudio - {titulo}',
                )

            link_cifra = self._safe_str(row.get('link_cifra', ''))
            if link_cifra:
                Cifra.objects.create(
                    musica=musica,
                    tipo_cifra='link',
                    link_referencia=link_cifra,
                )

        lote.log += f'\n[OK] Linha {row_num}: "{titulo}" importada com sucesso.'
        return musica

    def _criar_musica_from_dict(self, item: dict, lote: ImportacaoLote, idx: int) -> Musica:
        """Cria uma Musica a partir de um dicionário JSON."""
        titulo = str(item.get('titulo', '')).strip()
        if not titulo:
            raise ValueError(f'Título vazio no registro {idx}.')

        tom_raw = str(item.get('tom_principal', 'NI')).strip()
        if not tom_raw:
            tom_raw = 'NI'

        tom_normalizado = normalizar_tom(tom_raw)
        if tom_normalizado and tom_normalizado in VALID_TOMS:
            tom_principal = tom_normalizado
        elif tom_raw in VALID_TOMS:
            tom_principal = tom_raw
        else:
            tom_principal = 'NI'

        with transaction.atomic():
            musica = Musica.objects.create(
                titulo=titulo,
                subtitulo=item.get('subtitulo', ''),
                letra=item.get('letra', ''),
                tom_principal=tom_principal,
                observacoes=item.get('observacoes', ''),
                origem='importacao',
            )

            # Categorias
            for cat_nome in item.get('categorias', []):
                cat_nome = str(cat_nome).strip()
                if cat_nome:
                    cat, _ = CategoriaLiturgica.objects.get_or_create(
                        nome=cat_nome,
                        defaults={'descricao': '', 'ativo': True},
                    )
                    musica.categorias.add(cat)

            # Tags
            for tag_nome in item.get('tags', []):
                tag_nome = str(tag_nome).strip()
                if tag_nome:
                    tag, _ = Tag.objects.get_or_create(nome=tag_nome)
                    musica.tags.add(tag)

            # Links
            for link_data in item.get('links', []):
                LinkExterno.objects.create(
                    musica=musica,
                    url=link_data.get('url', ''),
                    tipo_conteudo=link_data.get('tipo_conteudo', 'referencia'),
                    provider=link_data.get('provider', 'generico'),
                    titulo_externo=link_data.get('titulo_externo', ''),
                    observacoes=link_data.get('observacoes', ''),
                )

            # Cifras (texto)
            for cifra_data in item.get('cifras', []):
                Cifra.objects.create(
                    musica=musica,
                    tipo_cifra=cifra_data.get('tipo_cifra', 'texto'),
                    conteudo_texto=cifra_data.get('conteudo_texto', ''),
                    link_referencia=cifra_data.get('link_referencia', ''),
                    tom=cifra_data.get('tom', ''),
                    observacoes=cifra_data.get('observacoes', ''),
                )

        lote.log += f'\n[OK] Registro {idx}: "{titulo}" importado com sucesso.'
        return musica

    def _vincular_midias_zip(self, base_dir: str, lote: ImportacaoLote):
        """Vincula arquivos de mídia encontrados no ZIP às músicas importadas."""
        pdfs_dir = os.path.join(base_dir, 'pdfs')
        audios_dir = os.path.join(base_dir, 'audios')
        cifras_dir = os.path.join(base_dir, 'cifras')

        if os.path.isdir(pdfs_dir):
            self._vincular_arquivos_por_pasta(
                pdfs_dir, 'pdf', lote,
            )

        if os.path.isdir(audios_dir):
            self._vincular_arquivos_por_pasta(
                audios_dir, 'audio', lote,
            )

        if os.path.isdir(cifras_dir):
            self._vincular_arquivos_por_pasta(
                cifras_dir, 'cifra', lote,
            )

    def _vincular_arquivos_por_pasta(
        self, pasta: str, tipo: str, lote: ImportacaoLote
    ):
        """Vincula arquivos de uma pasta às músicas pelo nome do arquivo."""
        for filename in os.listdir(pasta):
            filepath = os.path.join(pasta, filename)
            if not os.path.isfile(filepath):
                continue

            # Try to match filename (without extension) to a musica titulo
            nome_sem_ext = os.path.splitext(filename)[0].strip()
            musicas = Musica.objects.filter(titulo__iexact=nome_sem_ext, origem='importacao')
            if not musicas.exists():
                lote.log += (
                    f'\n[AVISO] Mídia "{filename}" ({tipo}): '
                    f'nenhuma música encontrada com título "{nome_sem_ext}".'
                )
                continue

            musica = musicas.first()
            with open(filepath, 'rb') as f:
                conteudo = ContentFile(f.read(), name=filename)

            try:
                if tipo == 'pdf':
                    PDFArquivo.objects.create(
                        musica=musica,
                        nome=nome_sem_ext,
                        arquivo=conteudo,
                    )
                elif tipo == 'audio':
                    AudioProprio.objects.create(
                        musica=musica,
                        nome=nome_sem_ext,
                        arquivo=conteudo,
                        tipo='referencia',
                    )
                elif tipo == 'cifra':
                    Cifra.objects.create(
                        musica=musica,
                        tipo_cifra='pdf',
                        arquivo_pdf=conteudo,
                    )
                lote.log += f'\n[OK] Mídia "{filename}" vinculada a "{musica.titulo}".'
            except Exception as e:
                lote.log += f'\n[ERRO] Mídia "{filename}": {e}'

        lote.save(update_fields=['log'])

    @staticmethod
    def _safe_str(value) -> str:
        """Converte valor para string limpa, tratando NaN do pandas."""
        if value is None:
            return ''
        s = str(value).strip()
        if s.lower() == 'nan':
            return ''
        return s


class ExportService:
    """Serviço para exportação de músicas em diversos formatos."""

    EXPORT_COLUMNS = [
        'titulo', 'subtitulo', 'tom_principal', 'categorias', 'tags',
        'observacoes', 'qtd_pdfs', 'qtd_audios', 'qtd_links', 'qtd_cifras',
    ]

    def _build_export_data(self, queryset) -> list[dict]:
        """Constrói lista de dicionários para exportação."""
        queryset = queryset.prefetch_related('categorias', 'tags', 'pdfs', 'audios', 'links_externos', 'cifras')
        data = []
        for musica in queryset:
            data.append({
                'titulo': musica.titulo,
                'subtitulo': musica.subtitulo,
                'tom_principal': musica.tom_principal,
                'categorias': ', '.join(c.nome for c in musica.categorias.all()),
                'tags': ', '.join(t.nome for t in musica.tags.all()),
                'observacoes': musica.observacoes,
                'qtd_pdfs': musica.pdfs.count(),
                'qtd_audios': musica.audios.count(),
                'qtd_links': musica.links_externos.count(),
                'qtd_cifras': musica.cifras.count(),
            })
        return data

    def exportar_csv(self, queryset) -> HttpResponse:
        """Exporta queryset de músicas para CSV."""
        data = self._build_export_data(queryset)
        df = pd.DataFrame(data, columns=self.EXPORT_COLUMNS)

        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')

        response = HttpResponse(
            buffer.getvalue().encode('utf-8-sig'),
            content_type='text/csv; charset=utf-8-sig',
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="musicas_{timestamp}.csv"'
        return response

    def exportar_excel(self, queryset) -> HttpResponse:
        """Exporta queryset de músicas para Excel (.xlsx)."""
        data = self._build_export_data(queryset)
        df = pd.DataFrame(data, columns=self.EXPORT_COLUMNS)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Músicas')
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="musicas_{timestamp}.xlsx"'
        return response

    def exportar_json(self, queryset) -> HttpResponse:
        """Exporta queryset de músicas para JSON (formato de backup completo)."""
        queryset = queryset.prefetch_related(
            'categorias', 'tags', 'pdfs', 'audios', 'links_externos', 'cifras',
        )

        dados = []
        for musica in queryset:
            registro = {
                'titulo': musica.titulo,
                'subtitulo': musica.subtitulo,
                'tom_principal': musica.tom_principal,
                'letra': musica.letra,
                'observacoes': musica.observacoes,
                'andamento': musica.andamento,
                'compasso': musica.compasso,
                'categorias': [c.nome for c in musica.categorias.all()],
                'tags': [t.nome for t in musica.tags.all()],
                'links': [
                    {
                        'url': link.url,
                        'tipo_conteudo': link.tipo_conteudo,
                        'provider': link.provider,
                        'titulo_externo': link.titulo_externo,
                        'observacoes': link.observacoes,
                    }
                    for link in musica.links_externos.all()
                ],
                'cifras': [
                    {
                        'tipo_cifra': cifra.tipo_cifra,
                        'conteudo_texto': cifra.conteudo_texto,
                        'link_referencia': cifra.link_referencia,
                        'tom': cifra.tom,
                        'observacoes': cifra.observacoes,
                    }
                    for cifra in musica.cifras.all()
                ],
            }
            dados.append(registro)

        json_str = json.dumps(dados, ensure_ascii=False, indent=2)

        response = HttpResponse(
            json_str,
            content_type='application/json; charset=utf-8',
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="musicas_{timestamp}.json"'
        return response

    def exportar_zip(self, queryset, incluir_midias: bool = False) -> HttpResponse:
        """Exporta queryset de músicas para ZIP com catálogo e opcionalmente mídias."""
        queryset = queryset.prefetch_related(
            'categorias', 'tags', 'pdfs', 'audios', 'links_externos', 'cifras',
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. catalogo.xlsx
            export_data = self._build_export_data(queryset)
            df = pd.DataFrame(export_data, columns=self.EXPORT_COLUMNS)
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Músicas')
            xlsx_buffer.seek(0)
            zf.writestr('catalogo.xlsx', xlsx_buffer.getvalue())

            # 2. metadata.json (full backup)
            dados_json = []
            for musica in queryset:
                registro = {
                    'titulo': musica.titulo,
                    'subtitulo': musica.subtitulo,
                    'tom_principal': musica.tom_principal,
                    'letra': musica.letra,
                    'observacoes': musica.observacoes,
                    'andamento': musica.andamento,
                    'compasso': musica.compasso,
                    'categorias': [c.nome for c in musica.categorias.all()],
                    'tags': [t.nome for t in musica.tags.all()],
                    'links': [
                        {
                            'url': link.url,
                            'tipo_conteudo': link.tipo_conteudo,
                            'provider': link.provider,
                            'titulo_externo': link.titulo_externo,
                        }
                        for link in musica.links_externos.all()
                    ],
                    'cifras': [
                        {
                            'tipo_cifra': cifra.tipo_cifra,
                            'conteudo_texto': cifra.conteudo_texto,
                            'link_referencia': cifra.link_referencia,
                            'tom': cifra.tom,
                        }
                        for cifra in musica.cifras.all()
                    ],
                }
                dados_json.append(registro)

            json_str = json.dumps(dados_json, ensure_ascii=False, indent=2)
            zf.writestr('metadata.json', json_str.encode('utf-8'))

            # 3. Mídias (opcional)
            if incluir_midias:
                for musica in queryset:
                    # PDFs
                    for pdf in musica.pdfs.all():
                        if pdf.arquivo:
                            try:
                                pdf.arquivo.open('rb')
                                zf.writestr(
                                    f'pdfs/{pdf.nome_arquivo}',
                                    pdf.arquivo.read(),
                                )
                                pdf.arquivo.close()
                            except Exception as e:
                                logger.warning(
                                    'Erro ao incluir PDF %s no ZIP: %s',
                                    pdf.nome_arquivo, e,
                                )

                    # Áudios
                    for audio in musica.audios.all():
                        if audio.arquivo:
                            try:
                                audio.arquivo.open('rb')
                                filename = os.path.basename(audio.arquivo.name)
                                zf.writestr(
                                    f'audios/{filename}',
                                    audio.arquivo.read(),
                                )
                                audio.arquivo.close()
                            except Exception as e:
                                logger.warning(
                                    'Erro ao incluir áudio %s no ZIP: %s',
                                    audio.nome, e,
                                )

                    # Cifras (PDFs)
                    for cifra in musica.cifras.all():
                        if cifra.arquivo_pdf:
                            try:
                                cifra.arquivo_pdf.open('rb')
                                filename = os.path.basename(cifra.arquivo_pdf.name)
                                zf.writestr(
                                    f'cifras/{filename}',
                                    cifra.arquivo_pdf.read(),
                                )
                                cifra.arquivo_pdf.close()
                            except Exception as e:
                                logger.warning(
                                    'Erro ao incluir cifra %s no ZIP: %s',
                                    filename, e,
                                )

        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/zip',
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="musicas_{timestamp}.zip"'
        return response
