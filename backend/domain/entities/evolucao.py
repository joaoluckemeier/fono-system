from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class StatusEvolucao(Enum):
    PENDENTE_REVISAO = "pendente_revisao"
    CONFIRMADA = "confirmada"


@dataclass
class Evolucao(EntidadeBase):
    paciente_id: UUID
    usuario_id: UUID
    data: date
    texto: str
    status: StatusEvolucao = StatusEvolucao.CONFIRMADA
    audio_ref: str | None = None
