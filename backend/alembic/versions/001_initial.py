"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_id'), 'workspaces', ['id'], unique=False)

    # Chat sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)

    # Chat messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('message_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_id'), 'chat_messages', ['id'], unique=False)

    # Files table
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('is_indexed', sa.Boolean(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('file_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_id'), 'files', ['id'], unique=False)

    # Flashcard sets table
    op.create_table(
        'flashcard_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flashcard_sets_id'), 'flashcard_sets', ['id'], unique=False)

    # Flashcards table
    op.create_table(
        'flashcards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('set_id', sa.Integer(), nullable=False),
        sa.Column('front', sa.Text(), nullable=False),
        sa.Column('back', sa.Text(), nullable=False),
        sa.Column('last_reviewed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('ease_factor', sa.Integer(), nullable=True),
        sa.Column('interval_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['set_id'], ['flashcard_sets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flashcards_id'), 'flashcards', ['id'], unique=False)

    # Exam sessions table
    op.create_table(
        'exam_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=200), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_sessions_id'), 'exam_sessions', ['id'], unique=False)

    # Exam questions table
    op.create_table(
        'exam_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['exam_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_questions_id'), 'exam_questions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_exam_questions_id'), table_name='exam_questions')
    op.drop_table('exam_questions')
    op.drop_index(op.f('ix_exam_sessions_id'), table_name='exam_sessions')
    op.drop_table('exam_sessions')
    op.drop_index(op.f('ix_flashcards_id'), table_name='flashcards')
    op.drop_table('flashcards')
    op.drop_index(op.f('ix_flashcard_sets_id'), table_name='flashcard_sets')
    op.drop_table('flashcard_sets')
    op.drop_index(op.f('ix_files_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_chat_messages_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_chat_sessions_id'), table_name='chat_sessions')
    op.drop_table('chat_sessions')
    op.drop_index(op.f('ix_workspaces_id'), table_name='workspaces')
    op.drop_table('workspaces')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

