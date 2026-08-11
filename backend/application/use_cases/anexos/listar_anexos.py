from uuid import UUID

from backend.application.dtos.anexo_dto import AnexoDTO, anexo_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import RECURSO_POR_ENTIDADE_ANEXO, usuario_pode
from backend.domain.entities.anexo import EntidadeAnexavel
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.anexo_repository import AnexoRepository


class ListarAnexosUseCase:
    def __init__(self, anexo_repository: AnexoRepository) -> None:
        self._anexo_repository = anexo_repository

    async def executar(
        self, entidade_tipo: str, entidade_id: UUID, clinica_id: UUID, papel: PapelUsuario
    ) -> list[AnexoDTO]:
        entidade = EntidadeAnexavel(entidade_tipo)
        recurso = RECURSO_POR_ENTIDADE_ANEXO[entidade]
        if not usuario_pode(papel, recurso):
            raise PermissaoNegadaError("Papel sem permissao para listar estes anexos")

        anexos = await self._anexo_repository.listar_por_entidade(
            entidade, entidade_id, clinica_id
        )
        return [anexo_to_dto(a) for a in anexos]
