from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class TarefaCreate(BaseModel):
    data: date
    titulo: str
    descricao: str | None = None
    prioridade: Literal["alta", "media", "baixa"] = "media"


class TarefaUpdate(BaseModel):
    data: date
    titulo: str
    descricao: str | None = None
    prioridade: Literal["alta", "media", "baixa"]


class MarcarConclusaoRequest(BaseModel):
    concluido: bool


class DuplicarTarefasRequest(BaseModel):
    tarefa_ids: list[UUID]
    nova_data: date


class TarefaResponse(BaseModel):
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


class TarefasPorPacienteResponse(BaseModel):
    paciente_id: UUID
    paciente_nome: str
    tarefas: list[TarefaResponse]
