from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.clinica import Clinica, PlanoClinica
from backend.domain.repositories.clinica_repository import ClinicaRepository
from backend.infrastructure.database.models.clinica_model import ClinicaModel


def _to_entity(model: ClinicaModel) -> Clinica:
    return Clinica(
        id=model.id,
        nome=model.nome,
        plano=PlanoClinica(model.plano),
        criado_em=model.criado_em,
    )


class ClinicaRepositoryImpl(ClinicaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, clinica: Clinica) -> Clinica:
        model = ClinicaModel(id=clinica.id, nome=clinica.nome, plano=clinica.plano.value)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID) -> Clinica | None:
        model = await self._session.get(ClinicaModel, id)
        return _to_entity(model) if model else None

    async def listar(self) -> list[Clinica]:
        result = await self._session.execute(select(ClinicaModel))
        return [_to_entity(m) for m in result.scalars().all()]
