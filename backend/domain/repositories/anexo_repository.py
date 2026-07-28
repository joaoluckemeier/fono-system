from abc import abstractmethod
from uuid import UUID

from backend.domain.entities.anexo import Anexo, EntidadeAnexavel
from backend.domain.repositories.base_repository import BaseRepository


class AnexoRepository(BaseRepository[Anexo]):
    @abstractmethod
    async def listar_por_entidade(
        self, entidade_tipo: EntidadeAnexavel, entidade_id: UUID, clinica_id: UUID
    ) -> list[Anexo]: ...
