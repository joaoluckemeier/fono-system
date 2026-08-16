import asyncio

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from backend.domain.services.gerador_documento_service import GeradorDocumentoInterface

_MARGEM_MM = 25
_LARGURA_ASSINATURA_MM = 80

# A fonte core (Helvetica) do fpdf2 so suporta Latin-1 - textos digitados/colados de editores
# como Word/Google Docs frequentemente trazem "aspas inteligentes", travessao e reticencias
# tipograficas fora desse charset, o que quebraria a geracao do PDF sem esse tratamento.
_SUBSTITUICOES_TIPOGRAFICAS = {
    "–": "-",  # en-dash
    "—": "-",  # em-dash
    "‘": "'",  # aspas simples curvas
    "’": "'",
    "“": '"',  # aspas duplas curvas
    "”": '"',
    "…": "...",  # reticencias
}


def _texto_seguro_pdf(texto: str) -> str:
    for original, substituto in _SUBSTITUICOES_TIPOGRAFICAS.items():
        texto = texto.replace(original, substituto)
    return texto.encode("latin-1", errors="replace").decode("latin-1")


def _montar_pdf(
    titulo: str,
    corpo_texto: str,
    nome_paciente: str,
    nome_profissional: str,
    data_atual: str,
) -> bytes:
    titulo = _texto_seguro_pdf(titulo)
    corpo_texto = _texto_seguro_pdf(corpo_texto)
    nome_paciente = _texto_seguro_pdf(nome_paciente)
    nome_profissional = _texto_seguro_pdf(nome_profissional)
    data_atual = _texto_seguro_pdf(data_atual)

    pdf = FPDF(format="A4")
    pdf.set_margins(left=_MARGEM_MM, top=_MARGEM_MM, right=_MARGEM_MM)
    pdf.set_auto_page_break(auto=True, margin=_MARGEM_MM)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", size=16)
    pdf.multi_cell(0, 10, titulo, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, corpo_texto, align="J", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(14)

    pdf.set_font("Helvetica", size=11)
    pdf.cell(
        0,
        6,
        f"Local e data: ______________________________, {data_atual}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(16)

    _bloco_assinatura(pdf, f"Assinatura do responsável/paciente\n{nome_paciente}")
    pdf.ln(14)
    _bloco_assinatura(pdf, f"Assinatura do profissional responsável\n{nome_profissional}")

    return bytes(pdf.output())


def _bloco_assinatura(pdf: FPDF, rotulo: str) -> None:
    x, y = pdf.get_x(), pdf.get_y()
    pdf.line(x, y, x + _LARGURA_ASSINATURA_MM, y)
    pdf.ln(3)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(_LARGURA_ASSINATURA_MM, 5, rotulo, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


class FPDFGeradorDocumento(GeradorDocumentoInterface):
    """fpdf2 e sincrono e pure-Python - a chamada roda em thread pool
    (asyncio.to_thread) para nao bloquear o event loop, mesmo padrao do MinIOStorageService."""

    async def gerar_pdf(
        self,
        titulo: str,
        corpo_texto: str,
        nome_paciente: str,
        nome_profissional: str,
        data_atual: str,
    ) -> bytes:
        return await asyncio.to_thread(
            _montar_pdf, titulo, corpo_texto, nome_paciente, nome_profissional, data_atual
        )
