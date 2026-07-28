from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.services.storage_service import StorageServiceInterface


class DeletarEvolucaoUseCase:
    """Permite corrigir uma evolucao confirmada por engano (ou descartar um rascunho
    de IA que nao serve). Soft delete - o registro fica no banco para auditoria."""

    def __init__(
        self,
        evolucao_repository: EvolucaoRepository,
        storage_service: StorageServiceInterface,
    ) -> None:
        self._evolucao_repository = evolucao_repository
        self._storage_service = storage_service

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> None:
        if not usuario_pode(papel, Recurso.EVOLUCAO):
            raise PermissaoNegadaError("Papel sem permissao para excluir evolucao clinica")

        evolucao = await self._evolucao_repository.buscar_por_id(id, clinica_id)
        if evolucao is None:
            raise RecursoNaoEncontradoError("Evolucao nao encontrada")

        if evolucao.audio_ref:
            await self._storage_service.deletar(evolucao.audio_ref)

        await self._evolucao_repository.soft_delete(id, clinica_id)
