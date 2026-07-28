from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.caa_dados import CaaDados


@dataclass
class AtualizarCaaInputDTO:
    usa_caa: bool
    protocolo_aip_aplicado: bool
    sistema_ajustado: bool
    observacoes: str | None = None


@dataclass
class CaaDadosDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    usa_caa: bool
    protocolo_aip_aplicado: bool
    sistema_ajustado: bool
    observacoes: str | None
    criado_em: datetime
    atualizado_em: datetime


def caa_dados_to_dto(caa: CaaDados) -> CaaDadosDTO:
    return CaaDadosDTO(
        id=caa.id,
        clinica_id=caa.clinica_id,
        paciente_id=caa.paciente_id,
        usa_caa=caa.usa_caa,
        protocolo_aip_aplicado=caa.protocolo_aip_aplicado,
        sistema_ajustado=caa.sistema_ajustado,
        observacoes=caa.observacoes,
        criado_em=caa.criado_em,
        atualizado_em=caa.atualizado_em,
    )
