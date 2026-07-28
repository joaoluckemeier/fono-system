from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Contrato comum a repositorios de entidades filhas de uma clinica.

    `clinica_id` e obrigatorio (nunca opcional) em todo metodo que toca dado
    sensivel: esquecer o filtro multi-tenant vira erro de tipo, nao bug silencioso.
    """

    @abstractmethod
    async def salvar(self, entidade: T) -> T: ...

    @abstractmethod
    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> T | None: ...

    @abstractmethod
    async def listar(self, clinica_id: UUID) -> list[T]: ...

    @abstractmethod
    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None: ...
