from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class ModeloTermoModel(Base, TenantMixin):
    __tablename__ = "modelos_termo"

    nome: Mapped[str] = mapped_column(String, nullable=False)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    corpo_texto: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
