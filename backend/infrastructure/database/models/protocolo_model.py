from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.database.models.base import Base, TenantMixin


class ProtocoloModel(Base, TenantMixin):
    __tablename__ = "protocolos"

    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
