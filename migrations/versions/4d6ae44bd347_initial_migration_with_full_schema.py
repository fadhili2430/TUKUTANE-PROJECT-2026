"""Initial migration with full schema

Revision ID: 4d6ae44bd347
Revises: 
Create Date: 2026-04-18 01:55:20.233697

"""
from alembic import op
import sqlalchemy as sa


revision = '4d6ae44bd347'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('campus_area',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=512), nullable=False),
        sa.Column('campus_area_id', sa.Integer(), nullable=False),
        sa.Column('reset_token', sa.String(length=100), nullable=True),
        sa.Column('reset_token_expiry', sa.DateTime(), nullable=True),
        sa.Column('fcm_token', sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(['campus_area_id'], ['campus_area.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table('user_activities',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activity.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'activity_id')
    )
    op.create_table('event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('campus_area_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('max_attendees', sa.Integer(), nullable=False),
        sa.Column('organiser_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activity.id'], ),
        sa.ForeignKeyConstraint(['campus_area_id'], ['campus_area.id'], ),
        sa.ForeignKeyConstraint(['organiser_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rsvp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'event_id', name='_user_event_uc')
    )


def downgrade():
    op.drop_table('rsvp')
    op.drop_table('event')
    op.drop_table('user_activities')
    op.drop_table('user')
    op.drop_table('campus_area')
    op.drop_table('activity')
