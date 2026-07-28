from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.profissional_caso import EspecialidadeProfissional, ProfissionalCaso
from backend.domain.repositories.profissional_caso_repository import ProfissionalCasoRepository
from backend.infrastructure.database.models.profissional_caso_model import ProfissionalCasoModel


def _to_entity(model: ProfissionalCasoModel) -> ProfissionalCaso:
    return ProfissionalCaso(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        nome=model.nome,
        especialidade=EspecialidadeProfissional(model.especialidade),
        contato=model.contato,
    )


class ProfissionalCasoRepositoryImpl(ProfissionalCasoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: ProfissionalCaso) -> ProfissionalCaso:
        model = await self._session.get(ProfissionalCasoModel, entidade.id)
        if model is None:
            model = ProfissionalCasoModel(
                id=entidade.id, clinica_id=entidade.clinica_id, paciente_id=entidade.paciente_id
            )
            self._session.add(model)

        model.nome = entidade.nome
        model.especialidade = entidade.especialidade.value
        model.contato = entidade.contato

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> ProfissionalCaso | None:
        result = await self._session.execute(
            select(ProfissionalCasoModel).where(
                ProfissionalCasoModel.id == id,
                ProfissionalCasoModel.clinica_id == clinica_id,
                ProfissionalCasoModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[ProfissionalCaso]:
        result = await self._session.execute(
            select(ProfissionalCasoModel).where(
                ProfissionalCasoModel.clinica_id == clinica_id,
                ProfissionalCasoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(ProfissionalCasoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_paciente(
        self, paciente_id: UUID, clinica_id: UUID
    ) -> list[ProfissionalCaso]:
        result = await self._session.execute(
            select(ProfissionalCasoModel).where(
                ProfissionalCasoModel.paciente_id == paciente_id,
                ProfissionalCasoModel.clinica_id == clinica_id,
                ProfissionalCasoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]
