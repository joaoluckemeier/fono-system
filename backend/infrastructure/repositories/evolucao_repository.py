from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.evolucao import Evolucao, StatusEvolucao
from backend.domain.repositories.evolucao_repository import EvolucaoRepository
from backend.infrastructure.database.models.evolucao_model import EvolucaoModel


def _to_entity(model: EvolucaoModel) -> Evolucao:
    return Evolucao(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        usuario_id=model.usuario_id,
        data=model.data,
        texto=model.texto,
        status=StatusEvolucao(model.status),
        audio_ref=model.audio_ref,
    )


class EvolucaoRepositoryImpl(EvolucaoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Evolucao) -> Evolucao:
        model = await self._session.get(EvolucaoModel, entidade.id)
        if model is None:
            model = EvolucaoModel(
                id=entidade.id,
                clinica_id=entidade.clinica_id,
                paciente_id=entidade.paciente_id,
                usuario_id=entidade.usuario_id,
            )
            self._session.add(model)

        model.data = entidade.data
        model.texto = entidade.texto
        model.status = entidade.status.value
        model.audio_ref = entidade.audio_ref

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Evolucao | None:
        result = await self._session.execute(
            select(EvolucaoModel).where(
                EvolucaoModel.id == id,
                EvolucaoModel.clinica_id == clinica_id,
                EvolucaoModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Evolucao]:
        result = await self._session.execute(
            select(EvolucaoModel).where(
                EvolucaoModel.clinica_id == clinica_id,
                EvolucaoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(EvolucaoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> list[Evolucao]:
        result = await self._session.execute(
            select(EvolucaoModel)
            .where(
                EvolucaoModel.paciente_id == paciente_id,
                EvolucaoModel.clinica_id == clinica_id,
                EvolucaoModel.deletado.is_(False),
            )
            .order_by(desc(EvolucaoModel.data))
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def buscar_ultima(self, paciente_id: UUID, clinica_id: UUID) -> Evolucao | None:
        result = await self._session.execute(
            select(EvolucaoModel)
            .where(
                EvolucaoModel.paciente_id == paciente_id,
                EvolucaoModel.clinica_id == clinica_id,
                EvolucaoModel.deletado.is_(False),
                EvolucaoModel.status == StatusEvolucao.CONFIRMADA.value,
            )
            .order_by(desc(EvolucaoModel.data))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
