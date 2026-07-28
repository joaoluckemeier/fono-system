from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.refresh_token import RefreshToken
from backend.domain.repositories.refresh_token_repository import RefreshTokenRepository
from backend.infrastructure.database.models.refresh_token_model import RefreshTokenModel


def _to_entity(model: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        usuario_id=model.usuario_id,
        token_hash=model.token_hash,
        expira_em=model.expira_em,
        revogado=model.revogado,
    )


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: RefreshToken) -> RefreshToken:
        model = await self._session.get(RefreshTokenModel, entidade.id)
        if model is None:
            model = RefreshTokenModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.usuario_id = entidade.usuario_id
        model.token_hash = entidade.token_hash
        model.expira_em = entidade.expira_em
        model.revogado = entidade.revogado

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.id == id,
                RefreshTokenModel.clinica_id == clinica_id,
                RefreshTokenModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[RefreshToken]:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.clinica_id == clinica_id,
                RefreshTokenModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(RefreshTokenModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def buscar_por_token_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def revogar(self, token_hash: str) -> None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return
        model.revogado = True
        await self._session.commit()
