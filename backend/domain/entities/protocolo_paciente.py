from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID

from backend.domain.entities.base import EntidadeBase


class StatusProtocoloPaciente(Enum):
    REALIZADO = "realizado"
    PLANEJADO = "planejado"


@dataclass
class ProtocoloPaciente(EntidadeBase):
    paciente_id: UUID
    protocolo_id: UUID
    status: StatusProtocoloPaciente
    data_realizacao: date | None = None
    observacao: str | None = None
