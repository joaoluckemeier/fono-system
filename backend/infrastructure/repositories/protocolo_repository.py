from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.protocolo import Protocolo
from backend.domain.repositories.protocolo_repository import ProtocoloRepository
from backend.infrastructure.database.models.protocolo_model import ProtocoloModel


def _to_entity(model: ProtocoloModel) -> Protocolo:
    return Protocolo(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        nome=model.nome,
        descricao=model.descricao,
    )


class ProtocoloRepositoryImpl(ProtocoloRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Protocolo) -> Protocolo:
        model = await self._session.get(ProtocoloModel, entidade.id)
        if model is None:
            model = ProtocoloModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.nome = entidade.nome
        model.descricao = entidade.descricao

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Protocolo | None:
        result = await self._session.execute(
            select(ProtocoloModel).where(
                ProtocoloModel.id == id,
                ProtocoloModel.clinica_id == clinica_id,
                ProtocoloModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Protocolo]:
        result = await self._session.execute(
            select(ProtocoloModel).where(
                ProtocoloModel.clinica_id == clinica_id,
                ProtocoloModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(ProtocoloModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()
