from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class PacienteModel(Base, TenantMixin):
    __tablename__ = "pacientes"

    nome_completo: Mapped[str] = mapped_column(String, nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    nome_mae: Mapped[str] = mapped_column(String, nullable=False)
    nome_pai: Mapped[str] = mapped_column(String, nullable=False)
    tem_irmaos: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="em_avaliacao", server_default="em_avaliacao"
    )
    nome_irmaos: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostico: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    faz_uso_medicamento: Mapped[str] = mapped_column(Text, nullable=False)
    consentimento_lgpd_assinado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    informacoes_nascimento: Mapped[str | None] = mapped_column(Text, nullable=True)
    queixa_principal: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
