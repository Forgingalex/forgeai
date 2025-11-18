"""Add study planner tables

Revision ID: 002_add_study_planner
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_study_planner'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Study plans table
    op.create_table(
        'study_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hours_per_day', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_plans_id'), 'study_plans', ['id'], unique=False)

    # Study sessions table
    op.create_table(
        'study_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=200), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['study_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_sessions_id'), 'study_sessions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_study_sessions_id'), table_name='study_sessions')
    op.drop_table('study_sessions')
    op.drop_index(op.f('ix_study_plans_id'), table_name='study_plans')
    op.drop_table('study_plans')

