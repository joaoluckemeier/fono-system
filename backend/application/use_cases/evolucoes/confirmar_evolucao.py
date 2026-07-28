from uuid import UUID

from backend.application.dtos.evolucao_dto import (
    ConfirmarEvolucaoInputDTO,
    EvolucaoDTO,
    evolucao_to_dto,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.evolucao import StatusEvolucao
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.domain.services.storage_service import StorageServiceInterface


class ConfirmarEvolucaoUseCase:
    """Transiciona um rascunho de IA (pendente_revisao) pra confirmada. A fono pode editar
    o texto antes de confirmar. O audio original e descartado do storage nesse momento -
    minimizacao de dado (decisao: manter enquanto pendente, apagar apos confirmar).
    """

    def __init__(
        self,
        evolucao_repository: EvolucaoRepository,
        storage_service: StorageServiceInterface,
    ) -> None:
        self._evolucao_repository = evolucao_repository
        self._storage_service = storage_service

    async def executar(
        self,
        id: UUID,
        dto: ConfirmarEvolucaoInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> EvolucaoDTO:
        if not usuario_pode(papel, Recurso.EVOLUCAO):
            raise PermissaoNegadaError("Papel sem permissao para confirmar evolucao clinica")

        evolucao = await self._evolucao_repository.buscar_por_id(id, clinica_id)
        if evolucao is None:
            raise RecursoNaoEncontradoError("Evolucao nao encontrada")

        if dto.texto_final:
            evolucao.texto = dto.texto_final
        evolucao.status = StatusEvolucao.CONFIRMADA

        if evolucao.audio_ref:
            await self._storage_service.deletar(evolucao.audio_ref)
            evolucao.audio_ref = None

        salvo = await self._evolucao_repository.salvar(evolucao)
        return evolucao_to_dto(salvo)
