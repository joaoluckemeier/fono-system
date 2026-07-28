from uuid import UUID

from backend.application.dtos.caa_dados_dto import CaaDadosDTO, caa_dados_to_dto
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.caa_dados_repository import CaaDadosRepository


class BuscarCaaUseCase:
    def __init__(self, caa_dados_repository: CaaDadosRepository) -> None:
        self._caa_dados_repository = caa_dados_repository

    async def executar(self, paciente_id: UUID, clinica_id: UUID, papel: PapelUsuario) -> CaaDadosDTO:
        if not usuario_pode(papel, Recurso.PACIENTE_CLINICO):
            raise PermissaoNegadaError("Papel sem permissao para ver dados de CAA")

        caa = await self._caa_dados_repository.buscar_por_paciente(paciente_id, clinica_id)
        if caa is None:
            raise RecursoNaoEncontradoError("Dados de CAA nao encontrados para este paciente")
        return caa_dados_to_dto(caa)
