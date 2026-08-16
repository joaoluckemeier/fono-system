from uuid import UUID

from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository


class DeletarModeloTermoUseCase:
    def __init__(self, modelo_termo_repository: ModeloTermoRepository) -> None:
        self._modelo_termo_repository = modelo_termo_repository

    async def executar(self, id: UUID, clinica_id: UUID, papel: PapelUsuario) -> None:
        if not usuario_pode(papel, Recurso.TERMO_MODELO):
            raise PermissaoNegadaError("Papel sem permissao para excluir modelo de termo")

        modelo = await self._modelo_termo_repository.buscar_por_id(id, clinica_id)
        if modelo is None:
            raise RecursoNaoEncontradoError("Modelo de termo nao encontrado")

        await self._modelo_termo_repository.soft_delete(id, clinica_id)
