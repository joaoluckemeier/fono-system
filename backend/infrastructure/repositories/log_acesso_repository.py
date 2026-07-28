from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.log_acesso import AcaoAuditoria, LogAcesso
from backend.domain.repositories.log_acesso_repository import LogAcessoRepository
from backend.infrastructure.database.models.log_acesso_model import LogAcessoModel


def _to_entity(model: LogAcessoModel) -> LogAcesso:
    return LogAcesso(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        usuario_id=model.usuario_id,
        acao=AcaoAuditoria(model.acao),
        entidade_tipo=model.entidade_tipo,
        entidade_id=model.entidade_id,
        ip_origem=model.ip_origem,
    )


class LogAcessoRepositoryImpl(LogAcessoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: LogAcesso) -> LogAcesso:
        model = LogAcessoModel(
            id=entidade.id,
            clinica_id=entidade.clinica_id,
            usuario_id=entidade.usuario_id,
            acao=entidade.acao.value,
            entidade_tipo=entidade.entidade_tipo,
            entidade_id=entidade.entidade_id,
            ip_origem=entidade.ip_origem,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> LogAcesso | None:
        result = await self._session.execute(
            select(LogAcessoModel).where(
                LogAcessoModel.id == id, LogAcessoModel.clinica_id == clinica_id
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[LogAcesso]:
        result = await self._session.execute(
            select(LogAcessoModel).where(LogAcessoModel.clinica_id == clinica_id)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(LogAcessoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()
