from datetime import UTC, datetime
from uuid import UUID, uuid4

from backend.application.dtos.modelo_termo_dto import (
    CriarModeloTermoInputDTO,
    ModeloTermoDTO,
    modelo_termo_to_dto,
)
from backend.application.exceptions import PermissaoNegadaError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.modelo_termo import ModeloTermo, TipoModeloTermo
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository


class CriarModeloTermoUseCase:
    def __init__(self, modelo_termo_repository: ModeloTermoRepository) -> None:
        self._modelo_termo_repository = modelo_termo_repository

    async def executar(
        self, dto: CriarModeloTermoInputDTO, clinica_id: UUID, papel: PapelUsuario
    ) -> ModeloTermoDTO:
        if not usuario_pode(papel, Recurso.TERMO_MODELO):
            raise PermissaoNegadaError("Papel sem permissao para cadastrar modelo de termo")

        agora = datetime.now(UTC)
        modelo = ModeloTermo(
            id=uuid4(),
            clinica_id=clinica_id,
            criado_em=agora,
            atualizado_em=agora,
            deletado=False,
            deletado_em=None,
            nome=dto.nome,
            tipo=TipoModeloTermo(dto.tipo),
            corpo_texto=dto.corpo_texto,
        )
        salvo = await self._modelo_termo_repository.salvar(modelo)
        return modelo_termo_to_dto(salvo)
