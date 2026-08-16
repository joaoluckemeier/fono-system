import asyncio

from fpdf import FPDF

from backend.domain.services.gerador_documento_service import GeradorDocumentoInterface


def _montar_pdf(titulo: str, corpo_texto: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", size=16)
    pdf.multi_cell(0, 10, titulo)
    pdf.ln(4)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, corpo_texto)
    return bytes(pdf.output())


class FPDFGeradorDocumento(GeradorDocumentoInterface):
    """fpdf2 e sincrono e pure-Python - a chamada roda em thread pool
    (asyncio.to_thread) para nao bloquear o event loop, mesmo padrao do MinIOStorageService."""

    async def gerar_pdf(self, titulo: str, corpo_texto: str) -> bytes:
        return await asyncio.to_thread(_montar_pdf, titulo, corpo_texto)
