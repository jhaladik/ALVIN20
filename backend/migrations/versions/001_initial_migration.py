# migrations/versions/001_initial_migration.py - Database Migration
"""Initial migration - create all tables

Revision ID: 001
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create user table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('plan', sa.String(length=20), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('tokens_limit', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_plan'), 'user', ['plan'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

    # Create billing_plan table
    op.create_table('billing_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('monthly_token_limit', sa.Integer(), nullable=False),
        sa.Column('max_projects', sa.Integer(), nullable=True),
        sa.Column('max_collaborators', sa.Integer(), nullable=True),
        sa.Column('monthly_price_cents', sa.Integer(), nullable=True),
        sa.Column('token_overage_price_per_1k_cents', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create project table
    op.create_table('project',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('genre', sa.String(length=50), nullable=True),
        sa.Column('current_phase', sa.String(length=20), nullable=True),
        sa.Column('target_word_count', sa.Integer(), nullable=True),
        sa.Column('current_word_count', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('tone', sa.String(length=50), nullable=True),
        sa.Column('target_audience', sa.String(length=50), nullable=True),
        sa.Column('estimated_scope', sa.String(length=50), nullable=True),
        sa.Column('marketability', sa.Integer(), nullable=True),
        sa.Column('original_idea', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_created_at'), 'project', ['created_at'], unique=False)
    op.create_index(op.f('ix_project_current_phase'), 'project', ['current_phase'], unique=False)
    op.create_index(op.f('ix_project_genre'), 'project', ['genre'], unique=False)
    op.create_index(op.f('ix_project_title'), 'project', ['title'], unique=False)
    op.create_index(op.f('ix_project_user_id'), 'project', ['user_id'], unique=False)

    # Create user_subscription table
    op.create_table('user_subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('tokens_used_this_period', sa.Integer(), nullable=True),
        sa.Column('tokens_purchased_this_period', sa.Integer(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['billing_plan.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create scene table
    op.create_table('scene',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scene_type', sa.String(length=50), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('conflict', sa.Text(), nullable=True),
        sa.Column('emotional_intensity', sa.Float(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('dialog_count', sa.Integer(), nullable=True),
        sa.Column('hook', sa.Text(), nullable=True),
        sa.Column('character_focus', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scene_order_index'), 'scene', ['order_index'], unique=False)
    op.create_index(op.f('ix_scene_project_id'), 'scene', ['project_id'], unique=False)
    op.create_index(op.f('ix_scene_scene_type'), 'scene', ['scene_type'], unique=False)

    # Create story_object table
    op.create_table('story_object',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('object_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('importance', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('first_appearance', sa.Integer(), nullable=True),
        sa.Column('symbolic_meaning', sa.Text(), nullable=True),
        sa.Column('character_role', sa.String(length=50), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_story_object_importance'), 'story_object', ['importance'], unique=False)
    op.create_index(op.f('ix_story_object_name'), 'story_object', ['name'], unique=False)
    op.create_index(op.f('ix_story_object_object_type'), 'story_object', ['object_type'], unique=False)
    op.create_index(op.f('ix_story_object_project_id'), 'story_object', ['project_id'], unique=False)
    op.create_index(op.f('ix_story_object_status'), 'story_object', ['status'], unique=False)

    # Create token_usage_log table
    op.create_table('token_usage_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_cost', sa.Integer(), nullable=False),
        sa.Column('multiplier', sa.Float(), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('operation_metadata', sa.JSON(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=50), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('billable', sa.Boolean(), nullable=True),
        sa.Column('billed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['scene_id'], ['scene.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_usage_log_created_at'), 'token_usage_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_token_usage_log_operation_type'), 'token_usage_log', ['operation_type'], unique=False)
    op.create_index(op.f('ix_token_usage_log_project_id'), 'token_usage_log', ['project_id'], unique=False)
    op.create_index(op.f('ix_token_usage_log_scene_id'), 'token_usage_log', ['scene_id'], unique=False)
    op.create_index(op.f('ix_token_usage_log_user_id'), 'token_usage_log', ['user_id'], unique=False)

    # Create token_purchase table
    op.create_table('token_purchase',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tokens_purchased', sa.Integer(), nullable=False),
        sa.Column('price_paid_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('payment_method', sa.String(length=20), nullable=True),
        sa.Column('payment_id', sa.String(length=100), nullable=True),
        sa.Column('payment_status', sa.String(length=20), nullable=True),
        sa.Column('purchase_reason', sa.String(length=100), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create project_collaborator table
    op.create_table('project_collaborator',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('invitation_token', sa.String(length=100), nullable=True),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.Column('invited_at', sa.DateTime(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('last_access', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invited_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='unique_project_user')
    )

    # Create comment table
    op.create_table('comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('thread_depth', sa.Integer(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('comment_type', sa.String(length=20), nullable=True),
        sa.Column('position_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comment.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['scene_id'], ['scene.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scene_object table
    op.create_table('scene_object',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('transformation', sa.Text(), nullable=True),
        sa.Column('significance', sa.String(length=20), nullable=True),
        sa.Column('interaction_type', sa.String(length=50), nullable=True),
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['object_id'], ['story_object.id'], ),
        sa.ForeignKeyConstraint(['scene_id'], ['scene.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scene_object_object_id'), 'scene_object', ['object_id'], unique=False)
    op.create_index(op.f('ix_scene_object_scene_id'), 'scene_object', ['scene_id'], unique=False)

def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_scene_object_scene_id'), table_name='scene_object')
    op.drop_index(op.f('ix_scene_object_object_id'), table_name='scene_object')
    op.drop_table('scene_object')
    op.drop_table('comment')
    op.drop_table('project_collaborator')
    op.drop_table('token_purchase')
    op.drop_index(op.f('ix_token_usage_log_user_id'), table_name='token_usage_log')
    op.drop_index(op.f('ix_token_usage_log_scene_id'), table_name='token_usage_log')
    op.drop_index(op.f('ix_token_usage_log_project_id'), table_name='token_usage_log')
    op.drop_index(op.f('ix_token_usage_log_operation_type'), table_name='token_usage_log')
    op.drop_index(op.f('ix_token_usage_log_created_at'), table_name='token_usage_log')
    op.drop_table('token_usage_log')
    op.drop_index(op.f('ix_story_object_status'), table_name='story_object')
    op.drop_index(op.f('ix_story_object_project_id'), table_name='story_object')
    op.drop_index(op.f('ix_story_object_object_type'), table_name='story_object')
    op.drop_index(op.f('ix_story_object_name'), table_name='story_object')
    op.drop_index(op.f('ix_story_object_importance'), table_name='story_object')
    op.drop_table('story_object')
    op.drop_index(op.f('ix_scene_scene_type'), table_name='scene')
    op.drop_index(op.f('ix_scene_project_id'), table_name='scene')
    op.drop_index(op.f('ix_scene_order_index'), table_name='scene')
    op.drop_table('scene')
    op.drop_table('user_subscription')
    op.drop_index(op.f('ix_project_user_id'), table_name='project')
    op.drop_index(op.f('ix_project_title'), table_name='project')
    op.drop_index(op.f('ix_project_genre'), table_name='project')
    op.drop_index(op.f('ix_project_current_phase'), table_name='project')
    op.drop_index(op.f('ix_project_created_at'), table_name='project')
    op.drop_table('project')
    op.drop_table('billing_plan')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_plan'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_table('user')