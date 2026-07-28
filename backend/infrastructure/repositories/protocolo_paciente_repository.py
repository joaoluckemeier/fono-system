from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.protocolo_paciente import ProtocoloPaciente, StatusProtocoloPaciente
from backend.domain.repositories.protocolo_paciente_repository import ProtocoloPacienteRepository
from backend.infrastructure.database.models.protocolo_paciente_model import ProtocoloPacienteModel


def _to_entity(model: ProtocoloPacienteModel) -> ProtocoloPaciente:
    return ProtocoloPaciente(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        paciente_id=model.paciente_id,
        protocolo_id=model.protocolo_id,
        status=StatusProtocoloPaciente(model.status),
        data_realizacao=model.data_realizacao,
        observacao=model.observacao,
    )


class ProtocoloPacienteRepositoryImpl(ProtocoloPacienteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: ProtocoloPaciente) -> ProtocoloPaciente:
        model = await self._session.get(ProtocoloPacienteModel, entidade.id)
        if model is None:
            model = ProtocoloPacienteModel(
                id=entidade.id,
                clinica_id=entidade.clinica_id,
                paciente_id=entidade.paciente_id,
                protocolo_id=entidade.protocolo_id,
            )
            self._session.add(model)

        model.status = entidade.status.value
        model.data_realizacao = entidade.data_realizacao
        model.observacao = entidade.observacao

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> ProtocoloPaciente | None:
        result = await self._session.execute(
            select(ProtocoloPacienteModel).where(
                ProtocoloPacienteModel.id == id,
                ProtocoloPacienteModel.clinica_id == clinica_id,
                ProtocoloPacienteModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[ProtocoloPaciente]:
        result = await self._session.execute(
            select(ProtocoloPacienteModel).where(
                ProtocoloPacienteModel.clinica_id == clinica_id,
                ProtocoloPacienteModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(ProtocoloPacienteModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_paciente(
        self, paciente_id: UUID, clinica_id: UUID
    ) -> list[ProtocoloPaciente]:
        result = await self._session.execute(
            select(ProtocoloPacienteModel).where(
                ProtocoloPacienteModel.paciente_id == paciente_id,
                ProtocoloPacienteModel.clinica_id == clinica_id,
                ProtocoloPacienteModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]
