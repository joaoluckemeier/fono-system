from uuid import UUID

from backend.application.dtos.anexo_dto import AnexoDTO, anexo_to_dto
from backend.domain.entities.anexo import EntidadeAnexavel
from backend.domain.repositories.anexo_repository import AnexoRepository


class ListarAnexosUseCase:
    def __init__(self, anexo_repository: AnexoRepository) -> None:
        self._anexo_repository = anexo_repository

    async def executar(
        self, entidade_tipo: str, entidade_id: UUID, clinica_id: UUID
    ) -> list[AnexoDTO]:
        anexos = await self._anexo_repository.listar_por_entidade(
            EntidadeAnexavel(entidade_tipo), entidade_id, clinica_id
        )
        return [anexo_to_dto(a) for a in anexos]
