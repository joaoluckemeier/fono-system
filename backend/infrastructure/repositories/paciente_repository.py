from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.paciente import Paciente, StatusPaciente
from backend.domain.repositories.paciente_repository import PacienteRepository
from backend.infrastructure.database.models.paciente_model import PacienteModel


def _to_entity(model: PacienteModel) -> Paciente:
    return Paciente(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        nome_completo=model.nome_completo,
        data_nascimento=model.data_nascimento,
        nome_mae=model.nome_mae,
        nome_pai=model.nome_pai,
        tem_irmaos=model.tem_irmaos,
        faz_uso_medicamento=model.faz_uso_medicamento,
        status=StatusPaciente(model.status),
        nome_irmaos=model.nome_irmaos,
        diagnostico=model.diagnostico,
        data_inicio_nipwin=model.data_inicio_nipwin,
        consentimento_lgpd_assinado_em=model.consentimento_lgpd_assinado_em,
    )


class PacienteRepositoryImpl(PacienteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Paciente) -> Paciente:
        model = await self._session.get(PacienteModel, entidade.id)
        if model is None:
            model = PacienteModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.nome_completo = entidade.nome_completo
        model.data_nascimento = entidade.data_nascimento
        model.nome_mae = entidade.nome_mae
        model.nome_pai = entidade.nome_pai
        model.tem_irmaos = entidade.tem_irmaos
        model.faz_uso_medicamento = entidade.faz_uso_medicamento
        model.status = entidade.status.value
        model.nome_irmaos = entidade.nome_irmaos
        model.diagnostico = entidade.diagnostico
        model.data_inicio_nipwin = entidade.data_inicio_nipwin
        model.consentimento_lgpd_assinado_em = entidade.consentimento_lgpd_assinado_em

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Paciente | None:
        result = await self._session.execute(
            select(PacienteModel).where(
                PacienteModel.id == id,
                PacienteModel.clinica_id == clinica_id,
                PacienteModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Paciente]:
        result = await self._session.execute(
            select(PacienteModel).where(
                PacienteModel.clinica_id == clinica_id,
                PacienteModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(PacienteModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()
