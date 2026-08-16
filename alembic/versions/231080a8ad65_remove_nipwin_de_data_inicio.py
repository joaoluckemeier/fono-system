"""remove nipwin de data_inicio

Revision ID: 231080a8ad65
Revises: c35f0e370575
Create Date: 2026-08-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '231080a8ad65'
down_revision: Union[str, None] = 'c35f0e370575'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('pacientes', 'data_inicio_nipwin', new_column_name='data_inicio')


def downgrade() -> None:
    op.alter_column('pacientes', 'data_inicio', new_column_name='data_inicio_nipwin')
