import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class AnexoModel(Base, TenantMixin):
    __tablename__ = "anexos"

    entidade_tipo: Mapped[str] = mapped_column(String, nullable=False)
    entidade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    tipo_arquivo: Mapped[str] = mapped_column(String, nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String, nullable=False)
    storage_ref: Mapped[str] = mapped_column(String, nullable=False)
    criado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
