from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.modelo_termo import ModeloTermo, TipoModeloTermo
from backend.domain.repositories.modelo_termo_repository import ModeloTermoRepository
from backend.infrastructure.database.models.modelo_termo_model import ModeloTermoModel


def _to_entity(model: ModeloTermoModel) -> ModeloTermo:
    return ModeloTermo(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        nome=model.nome,
        tipo=TipoModeloTermo(model.tipo),
        corpo_texto=model.corpo_texto,
        ativo=model.ativo,
    )


class ModeloTermoRepositoryImpl(ModeloTermoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: ModeloTermo) -> ModeloTermo:
        model = await self._session.get(ModeloTermoModel, entidade.id)
        if model is None:
            model = ModeloTermoModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.nome = entidade.nome
        model.tipo = entidade.tipo.value
        model.corpo_texto = entidade.corpo_texto
        model.ativo = entidade.ativo

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> ModeloTermo | None:
        result = await self._session.execute(
            select(ModeloTermoModel).where(
                ModeloTermoModel.id == id,
                ModeloTermoModel.clinica_id == clinica_id,
                ModeloTermoModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[ModeloTermo]:
        result = await self._session.execute(
            select(ModeloTermoModel).where(
                ModeloTermoModel.clinica_id == clinica_id,
                ModeloTermoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(ModeloTermoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()
