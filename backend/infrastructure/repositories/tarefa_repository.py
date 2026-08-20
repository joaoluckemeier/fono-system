from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.tarefa import PrioridadeTarefa, Tarefa
from backend.domain.repositories.tarefa_repository import TarefaRepository
from backend.infrastructure.database.models.tarefa_model import TarefaModel


def _to_entity(model: TarefaModel) -> Tarefa:
    return Tarefa(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        data=model.data,
        titulo=model.titulo,
        descricao=model.descricao,
        prioridade=PrioridadeTarefa(model.prioridade),
        concluido=model.concluido,
        concluido_em=model.concluido_em,
    )


class TarefaRepositoryImpl(TarefaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Tarefa) -> Tarefa:
        model = await self._session.get(TarefaModel, entidade.id)
        if model is None:
            model = TarefaModel(
                id=entidade.id,
                clinica_id=entidade.clinica_id,
                paciente_id=entidade.paciente_id,
            )
            self._session.add(model)

        model.data = entidade.data
        model.titulo = entidade.titulo
        model.descricao = entidade.descricao
        model.prioridade = entidade.prioridade.value
        model.concluido = entidade.concluido
        model.concluido_em = entidade.concluido_em

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Tarefa | None:
        result = await self._session.execute(
            select(TarefaModel).where(
                TarefaModel.id == id,
                TarefaModel.clinica_id == clinica_id,
                TarefaModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Tarefa]:
        result = await self._session.execute(
            select(TarefaModel).where(
                TarefaModel.clinica_id == clinica_id,
                TarefaModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(TarefaModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_paciente_periodo(
        self, paciente_id: UUID, clinica_id: UUID, data_inicio: date, data_fim: date
    ) -> list[Tarefa]:
        result = await self._session.execute(
            select(TarefaModel)
            .where(
                TarefaModel.paciente_id == paciente_id,
                TarefaModel.clinica_id == clinica_id,
                TarefaModel.deletado.is_(False),
                TarefaModel.data >= data_inicio,
                TarefaModel.data <= data_fim,
            )
            .order_by(TarefaModel.data)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def listar_por_periodo(
        self, clinica_id: UUID, data_inicio: date, data_fim: date
    ) -> list[Tarefa]:
        result = await self._session.execute(
            select(TarefaModel)
            .where(
                TarefaModel.clinica_id == clinica_id,
                TarefaModel.deletado.is_(False),
                TarefaModel.data >= data_inicio,
                TarefaModel.data <= data_fim,
            )
            .order_by(TarefaModel.paciente_id, TarefaModel.data)
        )
        return [_to_entity(m) for m in result.scalars().all()]
