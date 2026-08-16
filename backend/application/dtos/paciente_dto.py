from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.paciente import Paciente


@dataclass
class CriarPacienteInputDTO:
    nome_completo: str
    data_nascimento: date
    nome_mae: str
    nome_pai: str
    tem_irmaos: bool
    faz_uso_medicamento: str
    nome_irmaos: str | None = None
    diagnostico: str | None = None
    data_inicio: date | None = None
    consentimento_lgpd_assinado_em: datetime | None = None
    informacoes_nascimento: str | None = None
    queixa_principal: str | None = None
    observacoes: str | None = None


@dataclass
class AtualizarPacienteInputDTO(CriarPacienteInputDTO):
    pass


@dataclass
class AtualizarStatusPacienteInputDTO:
    status: str


@dataclass
class PacienteDTO:
    id: UUID
    clinica_id: UUID
    nome_completo: str
    data_nascimento: date
    nome_mae: str
    nome_pai: str
    tem_irmaos: bool
    status: str
    nome_irmaos: str | None
    diagnostico: str | None
    data_inicio: date | None
    faz_uso_medicamento: str
    consentimento_lgpd_assinado_em: datetime | None
    idade: int
    informacoes_nascimento: str | None
    queixa_principal: str | None
    observacoes: str | None
    criado_em: datetime
    atualizado_em: datetime


def paciente_to_dto(paciente: Paciente) -> PacienteDTO:
    return PacienteDTO(
        id=paciente.id,
        clinica_id=paciente.clinica_id,
        nome_completo=paciente.nome_completo,
        data_nascimento=paciente.data_nascimento,
        nome_mae=paciente.nome_mae,
        nome_pai=paciente.nome_pai,
        tem_irmaos=paciente.tem_irmaos,
        status=paciente.status.value,
        nome_irmaos=paciente.nome_irmaos,
        diagnostico=paciente.diagnostico,
        data_inicio=paciente.data_inicio,
        faz_uso_medicamento=paciente.faz_uso_medicamento,
        consentimento_lgpd_assinado_em=paciente.consentimento_lgpd_assinado_em,
        idade=paciente.idade,
        informacoes_nascimento=paciente.informacoes_nascimento,
        queixa_principal=paciente.queixa_principal,
        observacoes=paciente.observacoes,
        criado_em=paciente.criado_em,
        atualizado_em=paciente.atualizado_em,
    )
