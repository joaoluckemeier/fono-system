from uuid import UUID

from backend.application.dtos.modelo_termo_dto import (
    AtualizarModeloTermoInputDTO,
    ModeloTermoDTO,
    modelo_termo_to_dto,
)
from backend.application.exceptions import PermissaoNegadaError, RecursoNaoEncontradoError
from backend.domain.authorization.policy import Recurso, usuario_pode
from backend.domain.entities.modelo_termo import TipoModeloTermo
from backend.domain.entities.usuario import PapelUsuario
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository


class AtualizarModeloTermoUseCase:
    def __init__(self, modelo_termo_repository: ModeloTermoRepository) -> None:
        self._modelo_termo_repository = modelo_termo_repository

    async def executar(
        self,
        id: UUID,
        dto: AtualizarModeloTermoInputDTO,
        clinica_id: UUID,
        papel: PapelUsuario,
    ) -> ModeloTermoDTO:
        if not usuario_pode(papel, Recurso.TERMO_MODELO):
            raise PermissaoNegadaError("Papel sem permissao para editar modelo de termo")

        modelo = await self._modelo_termo_repository.buscar_por_id(id, clinica_id)
        if modelo is None:
            raise RecursoNaoEncontradoError("Modelo de termo nao encontrado")

        modelo.nome = dto.nome
        modelo.tipo = TipoModeloTermo(dto.tipo)
        modelo.corpo_texto = dto.corpo_texto
        modelo.ativo = dto.ativo

        salvo = await self._modelo_termo_repository.salvar(modelo)
        return modelo_termo_to_dto(salvo)
