from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ModeloTermoCreate(BaseModel):
    nome: str
    tipo: str
    corpo_texto: str


class ModeloTermoUpdate(BaseModel):
    nome: str
    tipo: str
    corpo_texto: str
    ativo: bool


class ModeloTermoResponse(BaseModel):
    id: UUID
    clinica_id: UUID
    nome: str
    tipo: str
    corpo_texto: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
