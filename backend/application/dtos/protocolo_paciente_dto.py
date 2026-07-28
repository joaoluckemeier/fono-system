from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.protocolo_paciente import ProtocoloPaciente


@dataclass
class CriarProtocoloPacienteInputDTO:
    protocolo_id: UUID
    status: str
    data_realizacao: date | None = None
    observacao: str | None = None


@dataclass
class AtualizarStatusProtocoloPacienteInputDTO:
    status: str
    data_realizacao: date | None = None


@dataclass
class ProtocoloPacienteDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    protocolo_id: UUID
    status: str
    data_realizacao: date | None
    observacao: str | None
    criado_em: datetime
    atualizado_em: datetime


def protocolo_paciente_to_dto(pp: ProtocoloPaciente) -> ProtocoloPacienteDTO:
    return ProtocoloPacienteDTO(
        id=pp.id,
        clinica_id=pp.clinica_id,
        paciente_id=pp.paciente_id,
        protocolo_id=pp.protocolo_id,
        status=pp.status.value,
        data_realizacao=pp.data_realizacao,
        observacao=pp.observacao,
        criado_em=pp.criado_em,
        atualizado_em=pp.atualizado_em,
    )
