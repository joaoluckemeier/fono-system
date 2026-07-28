import uuid

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class CaaDadosModel(Base, TenantMixin):
    __tablename__ = "caa_dados"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, unique=True
    )
    usa_caa: Mapped[bool] = mapped_column(Boolean, nullable=False)
    protocolo_aip_aplicado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sistema_ajustado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
