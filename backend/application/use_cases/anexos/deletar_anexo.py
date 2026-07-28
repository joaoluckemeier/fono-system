from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.anexo import EntidadeAnexavel
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.domain.services.storage_service import StorageServiceInterface

_RECURSO_POR_ENTIDADE = {
    EntidadeAnexavel.EVOLUCAO: Recurso.ANEXO_CLINICO,
    EntidadeAnexavel.PACIENTE: Recurso.ANEXO_NAO_CLINICO,
    EntidadeAnexavel.PROTOCOLO_PACIENTE: Recurso.ANEXO_NAO_CLINICO,
}


class DeletarAnexoUseCase:
    def __init__(
        self, anexo_repository: AnexoRepository, storage_service: StorageServiceInterface
    ) -> None:
        self._anexo_repository = anexo_repository
        self._storage_service = storage_service

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> None:
        anexo = await self._anexo_repository.buscar_por_id(id, clinica_id)
        if anexo is None:
            raise RecursoNaoEncontradoError("Anexo nao encontrado")

        recurso = _RECURSO_POR_ENTIDADE[anexo.entidade_tipo]
        if not usuario_pode(papel, recurso):
            raise PermissaoNegadaError("Papel sem permissao para excluir este anexo")

        await self._storage_service.deletar(anexo.storage_ref)
        await self._anexo_repository.soft_delete(id, clinica_id)
