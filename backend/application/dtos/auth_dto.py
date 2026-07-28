from dataclasses import dataclass
from uuid import UUID


@dataclass
class LoginInputDTO:
    email: str
    senha: str


@dataclass
class TokenParDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class UsuarioAutenticadoDTO:
    id: UUID
    clinica_id: UUID
    papel: str
    nome: str
    email: str
