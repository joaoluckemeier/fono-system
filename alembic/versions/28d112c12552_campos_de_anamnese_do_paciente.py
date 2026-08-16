"""campos de anamnese do paciente

Revision ID: 28d112c12552
Revises: 231080a8ad65
Create Date: 2026-08-16 00:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28d112c12552'
down_revision: Union[str, None] = '231080a8ad65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pacientes', sa.Column('informacoes_nascimento', sa.Text(), nullable=True))
    op.add_column('pacientes', sa.Column('queixa_principal', sa.Text(), nullable=True))
    op.add_column('pacientes', sa.Column('observacoes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('pacientes', 'observacoes')
    op.drop_column('pacientes', 'queixa_principal')
    op.drop_column('pacientes', 'informacoes_nascimento')
