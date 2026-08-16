from uuid import UUID

from backend.application.dtos.modelo_termo_dto import ModeloTermoDTO, modelo_termo_to_dto
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository


class ListarModelosTermoUseCase:
    def __init__(self, modelo_termo_repository: ModeloTermoRepository) -> None:
        self._modelo_termo_repository = modelo_termo_repository

    async def executar(
        self, clinica_id: UUID, papel: PapelUsuario, apenas_ativos: bool = False
    ) -> list[ModeloTermoDTO]:
        # Gerenciar o catalogo (TERMO_MODELO) e escolher um modelo ao gerar um documento
        # (TERMO_GERACAO) sao dois motivos legitimos e distintos para listar - ainda roteado
        # 100% pela politica central, so combina as duas permissoes ja existentes.
        pode_gerenciar = usuario_pode(papel, Recurso.TERMO_MODELO)
        pode_gerar = usuario_pode(papel, Recurso.TERMO_GERACAO)
        if not (pode_gerenciar or pode_gerar):
            raise PermissaoNegadaError("Papel sem permissao para listar modelos de termo")

        modelos = await self._modelo_termo_repository.listar(clinica_id)
        if apenas_ativos:
            modelos = [m for m in modelos if m.ativo]
        return [modelo_termo_to_dto(m) for m in modelos]
