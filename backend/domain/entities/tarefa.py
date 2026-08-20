from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class PrioridadeTarefa(Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


@dataclass
class Tarefa(EntidadeBase):
    paciente_id: UUID
    data: date
    titulo: str
    descricao: str | None = None
    prioridade: PrioridadeTarefa = PrioridadeTarefa.MEDIA
    concluido: bool = False
    concluido_em: datetime | None = None
