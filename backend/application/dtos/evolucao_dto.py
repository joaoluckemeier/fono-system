from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.evolucao import Evolucao


@dataclass
class CriarEvolucaoInputDTO:
    data: date
    texto: str


@dataclass
class ConfirmarEvolucaoInputDTO:
    texto_final: str | None = None


@dataclass
class EvolucaoDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    usuario_id: UUID
    data: date
    texto: str
    status: str
    criado_em: datetime
    atualizado_em: datetime


def evolucao_to_dto(evolucao: Evolucao) -> EvolucaoDTO:
    return EvolucaoDTO(
        id=evolucao.id,
        clinica_id=evolucao.clinica_id,
        paciente_id=evolucao.paciente_id,
        usuario_id=evolucao.usuario_id,
        data=evolucao.data,
        texto=evolucao.texto,
        status=evolucao.status.value,
        criado_em=evolucao.criado_em,
        atualizado_em=evolucao.atualizado_em,
    )
