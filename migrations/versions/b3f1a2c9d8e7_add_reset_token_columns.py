"""Add reset_token columns to user table (no-op: included in initial migration)

Revision ID: b3f1a2c9d8e7
Revises: 4d6ae44bd347
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'b3f1a2c9d8e7'
down_revision = '4d6ae44bd347'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('user')]
    with op.batch_alter_table('user', schema=None) as batch_op:
        if 'reset_token' not in columns:
            batch_op.add_column(sa.Column('reset_token', sa.String(length=100), nullable=True))
        if 'reset_token_expiry' not in columns:
            batch_op.add_column(sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))


def downgrade():
    pass
