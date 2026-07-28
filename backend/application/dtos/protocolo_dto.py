from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.protocolo import Protocolo


@dataclass
class CriarProtocoloInputDTO:
    nome: str
    descricao: str | None = None


@dataclass
class ProtocoloDTO:
    id: UUID
    clinica_id: UUID
    nome: str
    descricao: str | None
    criado_em: datetime
    atualizado_em: datetime


def protocolo_to_dto(protocolo: Protocolo) -> ProtocoloDTO:
    return ProtocoloDTO(
        id=protocolo.id,
        clinica_id=protocolo.clinica_id,
        nome=protocolo.nome,
        descricao=protocolo.descricao,
        criado_em=protocolo.criado_em,
        atualizado_em=protocolo.atualizado_em,
    )
