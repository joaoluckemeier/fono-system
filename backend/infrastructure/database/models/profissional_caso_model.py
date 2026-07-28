import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class ProfissionalCasoModel(Base, TenantMixin):
    __tablename__ = "profissionais_caso"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    especialidade: Mapped[str] = mapped_column(String, nullable=False)
    contato: Mapped[str | None] = mapped_column(String, nullable=True)
