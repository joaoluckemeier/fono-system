from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.entities.anexo import Anexo, EntidadeAnexavel, TipoArquivo
from backend.domain.repositories.anexo_repository import AnexoRepository
from backend.infrastructure.database.models.anexo_model import AnexoModel


def _to_entity(model: AnexoModel) -> Anexo:
    return Anexo(
        id=model.id,
        clinica_id=model.clinica_id,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        deletado=model.deletado,
        deletado_em=model.deletado_em,
        entidade_tipo=EntidadeAnexavel(model.entidade_tipo),
        entidade_id=model.entidade_id,
        tipo_arquivo=TipoArquivo(model.tipo_arquivo),
        nome_arquivo=model.nome_arquivo,
        storage_ref=model.storage_ref,
        criado_por=model.criado_por,
    )


class AnexoRepositoryImpl(AnexoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def salvar(self, entidade: Anexo) -> Anexo:
        model = AnexoModel(
            id=entidade.id,
            clinica_id=entidade.clinica_id,
            entidade_tipo=entidade.entidade_tipo.value,
            entidade_id=entidade.entidade_id,
            tipo_arquivo=entidade.tipo_arquivo.value,
            nome_arquivo=entidade.nome_arquivo,
            storage_ref=entidade.storage_ref,
            criado_por=entidade.criado_por,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def buscar_por_id(self, id: UUID, clinica_id: UUID) -> Anexo | None:
        result = await self._session.execute(
            select(AnexoModel).where(
                AnexoModel.id == id,
                AnexoModel.clinica_id == clinica_id,
                AnexoModel.deletado.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, clinica_id: UUID) -> list[Anexo]:
        result = await self._session.execute(
            select(AnexoModel).where(
                AnexoModel.clinica_id == clinica_id,
                AnexoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def soft_delete(self, id: UUID, clinica_id: UUID) -> None:
        model = await self._session.get(AnexoModel, id)
        if model is None or model.clinica_id != clinica_id:
            return
        model.deletado = True
        model.deletado_em = datetime.now()
        await self._session.commit()

    async def listar_por_entidade(
        self, entidade_tipo: EntidadeAnexavel, entidade_id: UUID, clinica_id: UUID
    ) -> list[Anexo]:
        result = await self._session.execute(
            select(AnexoModel).where(
                AnexoModel.entidade_tipo == entidade_tipo.value,
                AnexoModel.entidade_id == entidade_id,
                AnexoModel.clinica_id == clinica_id,
                AnexoModel.deletado.is_(False),
            )
        )
        return [_to_entity(m) for m in result.scalars().all()]
