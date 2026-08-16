from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.termo_gerado import TermoGerado


@dataclass
class GerarTermoInputDTO:
    modelo_id: UUID


@dataclass
class TermoGeradoDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    modelo_id: UUID
    anexo_id: UUID
    gerado_por: UUID
    criado_em: datetime
    atualizado_em: datetime


@dataclass
class GerarTermoResultDTO:
    pdf_bytes: bytes
    termo: TermoGeradoDTO


def termo_gerado_to_dto(termo: TermoGerado) -> TermoGeradoDTO:
    return TermoGeradoDTO(
        id=termo.id,
        clinica_id=termo.clinica_id,
        paciente_id=termo.paciente_id,
        modelo_id=termo.modelo_id,
        anexo_id=termo.anexo_id,
        gerado_por=termo.gerado_por,
        criado_em=termo.criado_em,
        atualizado_em=termo.atualizado_em,
    )
