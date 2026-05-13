"""Add fcm_token column to user table

Revision ID: c4e2b3d1f9a8
Revises: b3f1a2c9d8e7
Create Date: 2026-05-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c4e2b3d1f9a8'
down_revision = 'b3f1a2c9d8e7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fcm_token', sa.String(length=256), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('fcm_token')
