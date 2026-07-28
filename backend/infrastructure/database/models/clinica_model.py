import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base


class ClinicaModel(Base):
    """Tabela raiz - nao usa TenantMixin (nao tem clinica_id nem soft delete)."""

    __tablename__ = "clinicas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    plano: Mapped[str] = mapped_column(String, nullable=False, default="basico")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
