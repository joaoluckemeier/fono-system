from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.usuario import PapelUsuario, Usuario
from backend.domain.repositories.usuario_repository import UsuarioRepository
from backend.infrastructure.database.models.usuario_model import UsuarioModel


def _to_entity(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        email=model.email,
        senha_hash=model.senha_hash,
        nome=model.nome,
        papel=PapelUsuario(model.papel),
        ativo=model.ativo,
        ultimo_login_em=model.ultimo_login_em,
    )


class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Usuario) -> Usuario:
        model = await self._session.get(UsuarioModel, entidade.id)
        if model is None:
            model = UsuarioModel(id=entidade.id, clinica_id=entidade.clinica_id)
            self._session.add(model)

        model.email = entidade.email
        model.senha_hash = entidade.senha_hash
        model.nome = entidade.nome
        model.papel = entidade.papel.value
        model.ativo = entidade.ativo
        model.ultimo_login_em = entidade.ultimo_login_em

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Usuario | None:
        result = await self._session.execute(
            select(UsuarioModel).where(
                UsuarioModel.id == id,
                UsuarioModel.clinica_id == clinica_id,
                UsuarioModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Usuario]:
        result = await self._session.execute(
            select(UsuarioModel).where(
                UsuarioModel.clinica_id == clinica_id,
                UsuarioModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(UsuarioModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def buscar_por_email(self, email: str) -> Usuario | None:
        result = await self._session.execute(
            select(UsuarioModel).where(
                UsuarioModel.email == email,
                UsuarioModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
