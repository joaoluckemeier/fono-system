"""termos e encaminhamentos

Revision ID: 5d6afb1bd31e
Revises: 28d112c12552
Create Date: 2026-08-16 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d6afb1bd31e'
down_revision: Union[str, None] = '28d112c12552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'modelos_termo',
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('corpo_texto', sa.Text(), nullable=False),
        sa.Column('ativo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('clinica_id', sa.UUID(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deletado', sa.Boolean(), nullable=False),
        sa.Column('deletado_em', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['clinica_id'], ['clinicas.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_modelos_termo_clinica_id'), 'modelos_termo', ['clinica_id'], unique=False)

    op.create_table(
        'termos_gerados',
        sa.Column('paciente_id', sa.UUID(), nullable=False),
        sa.Column('modelo_id', sa.UUID(), nullable=False),
        sa.Column('anexo_id', sa.UUID(), nullable=False),
        sa.Column('gerado_por', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('clinica_id', sa.UUID(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deletado', sa.Boolean(), nullable=False),
        sa.Column('deletado_em', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['clinica_id'], ['clinicas.id'], ),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
        sa.ForeignKeyConstraint(['modelo_id'], ['modelos_termo.id'], ),
        sa.ForeignKeyConstraint(['anexo_id'], ['anexos.id'], ),
        sa.ForeignKeyConstraint(['gerado_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_termos_gerados_clinica_id'), 'termos_gerados', ['clinica_id'], unique=False)
    op.create_index(op.f('ix_termos_gerados_paciente_id'), 'termos_gerados', ['paciente_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_termos_gerados_paciente_id'), table_name='termos_gerados')
    op.drop_index(op.f('ix_termos_gerados_clinica_id'), table_name='termos_gerados')
    op.drop_table('termos_gerados')
    op.drop_index(op.f('ix_modelos_termo_clinica_id'), table_name='modelos_termo')
    op.drop_table('modelos_termo')
