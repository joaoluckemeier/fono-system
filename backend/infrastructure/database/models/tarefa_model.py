import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class TarefaModel(Base, TenantMixin):
    __tablename__ = "tarefas_planejamento"
    __table_args__ = (
        Index("ix_tarefas_planejamento_clinica_paciente_data", "clinica_id", "paciente_id", "data"),
        Index("ix_tarefas_planejamento_clinica_data", "clinica_id", "data"),
    )

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    prioridade: Mapped[str] = mapped_column(
        String, nullable=False, default="media", server_default="media"
    )
    concluido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
