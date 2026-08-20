"""planejamento terapeutico semanal

Revision ID: df290f9c80f1
Revises: 5d6afb1bd31e
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df290f9c80f1'
down_revision: Union[str, None] = '5d6afb1bd31e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tarefas_planejamento',
        sa.Column('paciente_id', sa.UUID(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('prioridade', sa.String(), server_default='media', nullable=False),
        sa.Column('concluido', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('concluido_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('clinica_id', sa.UUID(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deletado', sa.Boolean(), nullable=False),
        sa.Column('deletado_em', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['clinica_id'], ['clinicas.id'], ),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_tarefas_planejamento_clinica_id'), 'tarefas_planejamento', ['clinica_id'], unique=False
    )
    op.create_index(
        op.f('ix_tarefas_planejamento_paciente_id'), 'tarefas_planejamento', ['paciente_id'], unique=False
    )
    op.create_index(
        op.f('ix_tarefas_planejamento_data'), 'tarefas_planejamento', ['data'], unique=False
    )
    op.create_index(
        'ix_tarefas_planejamento_clinica_paciente_data',
        'tarefas_planejamento',
        ['clinica_id', 'paciente_id', 'data'],
        unique=False,
    )
    op.create_index(
        'ix_tarefas_planejamento_clinica_data',
        'tarefas_planejamento',
        ['clinica_id', 'data'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_tarefas_planejamento_clinica_data', table_name='tarefas_planejamento')
    op.drop_index('ix_tarefas_planejamento_clinica_paciente_data', table_name='tarefas_planejamento')
    op.drop_index(op.f('ix_tarefas_planejamento_data'), table_name='tarefas_planejamento')
    op.drop_index(op.f('ix_tarefas_planejamento_paciente_id'), table_name='tarefas_planejamento')
    op.drop_index(op.f('ix_tarefas_planejamento_clinica_id'), table_name='tarefas_planejamento')
    op.drop_table('tarefas_planejamento')
