from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import RECURSO_POR_ENTIDADE_ANEXO, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.services.storage_service import StorageServiceInterface


class BuscarUrlAnexoUseCase:
    def __init__(
        self, anexo_repository: AnexoRepository, storage_service: StorageServiceInterface
    ) -> None:
        self._anexo_repository = anexo_repository
        self._storage_service = storage_service

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> str:
        anexo = await self._anexo_repository.buscar_por_id(id, clinica_id)
        if anexo is None:
            raise RecursoNaoEncontradoError("Anexo nao encontrado")

        recurso = RECURSO_POR_ENTIDADE_ANEXO[anexo.entidade_tipo]
        if not usuario_pode(papel, recurso):
            raise PermissaoNegadaError("Papel sem permissao para visualizar este anexo")

        return await self._storage_service.obter_url(anexo.storage_ref)
