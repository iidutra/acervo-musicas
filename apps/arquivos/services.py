"""Servico de extracao de texto de PDFs usando PyMuPDF."""
import logging

logger = logging.getLogger(__name__)


def extrair_texto_pdf(
    arquivo_path: str,
    pagina_inicial: int = None,
    pagina_final: int = None,
) -> str:
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    Returns extracted text or empty string on failure.
    This extraction is ASSISTIVE - not authoritative.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(arquivo_path)
        text_parts = []

        start = (pagina_inicial - 1) if pagina_inicial else 0
        end = pagina_final if pagina_final else len(doc)

        for page_num in range(start, min(end, len(doc))):
            page = doc[page_num]
            text_parts.append(page.get_text())

        doc.close()
        return '\n'.join(text_parts).strip()
    except Exception as e:
        logger.warning(f'Erro ao extrair texto do PDF {arquivo_path}: {e}')
        return ''
