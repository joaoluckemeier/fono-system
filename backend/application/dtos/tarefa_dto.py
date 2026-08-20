from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from backend.domain.entities.tarefa import Tarefa


@dataclass
class CriarTarefaInputDTO:
    data: date
    titulo: str
    descricao: str | None = None
    prioridade: str = "media"


@dataclass
class AtualizarTarefaInputDTO:
    data: date
    titulo: str
    descricao: str | None
    prioridade: str


@dataclass
class DuplicarTarefasInputDTO:
    tarefa_ids: list[UUID]
    nova_data: date


@dataclass
class TarefaDTO:
    id: UUID
    clinica_id: UUID
    paciente_id: UUID
    data: date
    titulo: str
    descricao: str | None
    prioridade: str
    concluido: bool
    concluido_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime


def tarefa_to_dto(tarefa: Tarefa) -> TarefaDTO:
    return TarefaDTO(
        id=tarefa.id,
        clinica_id=tarefa.clinica_id,
        paciente_id=tarefa.paciente_id,
        data=tarefa.data,
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        prioridade=tarefa.prioridade.value,
        concluido=tarefa.concluido,
        concluido_em=tarefa.concluido_em,
        criado_em=tarefa.criado_em,
        atualizado_em=tarefa.atualizado_em,
    )


@dataclass
class TarefasPorPacienteDTO:
    """Um 'card de paciente' na visao agregada semanal."""

    paciente_id: UUID
    paciente_nome: str
    tarefas: list[TarefaDTO]
