"""Add fcm_token column to user table (no-op: included in initial migration)

Revision ID: c4e2b3d1f9a8
Revises: b3f1a2c9d8e7
Create Date: 2026-05-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'c4e2b3d1f9a8'
down_revision = 'b3f1a2c9d8e7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('user')]
    with op.batch_alter_table('user', schema=None) as batch_op:
        if 'fcm_token' not in columns:
            batch_op.add_column(sa.Column('fcm_token', sa.String(length=256), nullable=True))


def downgrade():
    pass
