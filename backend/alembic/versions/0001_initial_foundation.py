"""initial_foundation

Revision ID: 0001_initial_foundation
Revises: 
Create Date: 2026-09-11 14:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_foundation'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'system_audit',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('component', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_system_audit_id', 'system_audit', ['id'], unique=False)
    op.create_index('ix_system_audit_event_type', 'system_audit', ['event_type'], unique=False)
    op.create_index('ix_system_audit_component', 'system_audit', ['component'], unique=False)
    op.create_index('ix_system_audit_recorded_at', 'system_audit', ['recorded_at'], unique=False)
    op.create_index('idx_system_audit_event_recorded', 'system_audit', ['event_type', 'recorded_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_system_audit_event_recorded', table_name='system_audit')
    op.drop_index('ix_system_audit_recorded_at', table_name='system_audit')
    op.drop_index('ix_system_audit_component', table_name='system_audit')
    op.drop_index('ix_system_audit_event_type', table_name='system_audit')
    op.drop_index('ix_system_audit_id', table_name='system_audit')
    op.drop_table('system_audit')
