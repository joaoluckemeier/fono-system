from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.termo_gerado import TermoGerado
from backend.domain.repositories.termo_gerado_repository import TermoGeradoRepository
from backend.infrastructure.database.models.termo_gerado_model import TermoGeradoModel


def _to_entity(model: TermoGeradoModel) -> TermoGerado:
    return TermoGerado(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        modelo_id=model.modelo_id,
        anexo_id=model.anexo_id,
        gerado_por=model.gerado_por,
    )


class TermoGeradoRepositoryImpl(TermoGeradoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: TermoGerado) -> TermoGerado:
        model = await self._session.get(TermoGeradoModel, entidade.id)
        if model is None:
            model = TermoGeradoModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.paciente_id = entidade.paciente_id
        model.modelo_id = entidade.modelo_id
        model.anexo_id = entidade.anexo_id
        model.gerado_por = entidade.gerado_por

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> TermoGerado | None:
        result = await self._session.execute(
            select(TermoGeradoModel).where(
                TermoGeradoModel.id == id,
                TermoGeradoModel.clinica_id == clinica_id,
                TermoGeradoModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[TermoGerado]:
        result = await self._session.execute(
            select(TermoGeradoModel).where(
                TermoGeradoModel.clinica_id == clinica_id,
                TermoGeradoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(TermoGeradoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> list[TermoGerado]:
        result = await self._session.execute(
            select(TermoGeradoModel).where(
                TermoGeradoModel.paciente_id == paciente_id,
                TermoGeradoModel.clinica_id == clinica_id,
                TermoGeradoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]
