from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.caa_dados import CaaDados
from backend.domain.repositories.caa_dados_repository import CaaDadosRepository
from backend.infrastructure.database.models.caa_dados_model import CaaDadosModel


def _to_entity(model: CaaDadosModel) -> CaaDados:
    return CaaDados(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        usa_caa=model.usa_caa,
        protocolo_aip_aplicado=model.protocolo_aip_aplicado,
        sistema_ajustado=model.sistema_ajustado,
        observacoes=model.observacoes,
    )


class CaaDadosRepositoryImpl(CaaDadosRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: CaaDados) -> CaaDados:
        model = await self._session.get(CaaDadosModel, entidade.id)
        if model is None:
            model = CaaDadosModel(
                id=entidade.id, clinica_id=entidade.clinica_id, paciente_id=entidade.paciente_id
            )
            self._session.add(model)

        model.usa_caa = entidade.usa_caa
        model.protocolo_aip_aplicado = entidade.protocolo_aip_aplicado
        model.sistema_ajustado = entidade.sistema_ajustado
        model.observacoes = entidade.observacoes

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> CaaDados | None:
        result = await self._session.execute(
            select(CaaDadosModel).where(
                CaaDadosModel.id == id,
                CaaDadosModel.clinica_id == clinica_id,
                CaaDadosModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[CaaDados]:
        result = await self._session.execute(
            select(CaaDadosModel).where(
                CaaDadosModel.clinica_id == clinica_id,
                CaaDadosModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(CaaDadosModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def buscar_por_paciente(self, paciente_id: UUID, clinica_id: UUID) -> CaaDados | None:
        result = await self._session.execute(
            select(CaaDadosModel).where(
                CaaDadosModel.paciente_id == paciente_id,
                CaaDadosModel.clinica_id == clinica_id,
                CaaDadosModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
