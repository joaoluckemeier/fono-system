from uuid import UUID

from backend.application.dtos.evolucao_dto import EvolucaoDTO, evolucao_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.evolucao_repository import EvolucaoRepository


class BuscarUltimaDevolutivaUseCase:
    def __init__(self, evolucao_repository: EvolucaoRepository) -> None:
        self._evolucao_repository = evolucao_repository

    async def executar(self, paciente_id: UUID, clinica_id: UUID, papel: PapelUsuario) -> EvolucaoDTO:
        if not usuario_pode(papel, Recurso.EVOLUCAO):
            raise PermissaoNegadaError("Papel sem permissao para ver evolucoes")

        ultima = await self._evolucao_repository.buscar_ultima(paciente_id, clinica_id)
        if ultima is None:
            raise RecursoNaoEncontradoError("Nenhuma evolucao registrada para este paciente")
        return evolucao_to_dto(ultima)
