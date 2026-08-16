from uuid import UUID

from backend.application.dtos.termo_gerado_dto import TermoGeradoDTO, termo_gerado_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.termo_gerado_repository import TermoGeradoRepository


class ListarTermosGeradosUseCase:
    def __init__(self, termo_gerado_repository: TermoGeradoRepository) -> None:
        self._termo_gerado_repository = termo_gerado_repository

    async def executar(
        self, paciente_id: UUID, clinica_id: UUID, papel: PapelUsuario
    ) -> list[TermoGeradoDTO]:
        if not usuario_pode(papel, Recurso.TERMO_GERACAO):
            raise PermissaoNegadaError("Papel sem permissao para ver historico de termos")

        termos = await self._termo_gerado_repository.listar_por_paciente(paciente_id, clinica_id)
        return [termo_gerado_to_dto(t) for t in termos]
