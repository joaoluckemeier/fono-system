from abc import abstractmethod

from backend.domain.entities.usuario import Usuario
from backend.domain.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    @abstractmethod
    async def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca cross-tenant: usado apenas no login, que ainda nao sabe a clinica_id.

        Email e unique por clinica (nao globalmente) - ver docs/modelagem.md. Enquanto
        so existe uma clinica em producao isso e inofensivo; se/quando emails duplicados
        entre clinicas existirem, o fluxo de login precisara pedir a clinica explicitamente.
        """
        ...
