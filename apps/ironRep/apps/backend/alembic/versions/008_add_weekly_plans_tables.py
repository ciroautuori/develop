"""Add weekly plans tables for Coach, Medical, Nutrition

Revision ID: 008
Revises: 007
Create Date: 2024-11-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # WeeklyPlanModel - unified weekly plan
    op.create_table(
        'weekly_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('coach_plan_id', sa.String(36), nullable=True),
        sa.Column('medical_plan_id', sa.String(36), nullable=True),
        sa.Column('nutrition_plan_id', sa.String(36), nullable=True),
        sa.Column('coach_summary', sa.JSON(), nullable=True),
        sa.Column('medical_summary', sa.JSON(), nullable=True),
        sa.Column('nutrition_summary', sa.JSON(), nullable=True),
        sa.Column('review_completed', sa.Boolean(), server_default='false'),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('ai_suggestions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_weekly_plans_user_week', 'weekly_plans', ['user_id', 'year', 'week_number'])

    # MedicalProtocolModel
    op.create_table(
        'medical_protocols',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('phase', sa.String(100), nullable=False),
        sa.Column('phase_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('target_pain_reduction', sa.Float(), nullable=True),
        sa.Column('starting_pain_level', sa.Float(), nullable=True),
        sa.Column('ending_pain_level', sa.Float(), nullable=True),
        sa.Column('daily_exercises', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('restrictions', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('checkin_frequency', sa.String(20), server_default='daily'),
        sa.Column('checkins_required', sa.Integer(), server_default='7'),
        sa.Column('checkins_completed', sa.Integer(), server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_medical_protocols_user_week', 'medical_protocols', ['user_id', 'year', 'week_number'])

    # CoachWeeklyPlanModel
    op.create_table(
        'coach_weekly_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('focus', sa.String(255), nullable=True),
        sa.Column('sport_type', sa.String(50), nullable=True),
        sa.Column('sessions', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('total_sessions', sa.Integer(), server_default='0'),
        sa.Column('completed_sessions', sa.Integer(), server_default='0'),
        sa.Column('total_volume', sa.Integer(), nullable=True),
        sa.Column('medical_constraints', sa.JSON(), nullable=True),
        sa.Column('max_intensity_percent', sa.Integer(), server_default='100'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_coach_weekly_plans_user_week', 'coach_weekly_plans', ['user_id', 'year', 'week_number'])

    # NutritionWeeklyPlanModel
    op.create_table(
        'nutrition_weekly_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('week_number', sa.Integer(), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('goal', sa.String(50), nullable=False, server_default='maintenance'),
        sa.Column('daily_calories', sa.Integer(), nullable=False),
        sa.Column('daily_protein', sa.Integer(), nullable=False),
        sa.Column('daily_carbs', sa.Integer(), nullable=False),
        sa.Column('daily_fat', sa.Integer(), nullable=False),
        sa.Column('water_target_liters', sa.Float(), server_default='2.5'),
        sa.Column('daily_meals', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('diet_type', sa.String(50), nullable=True),
        sa.Column('excluded_foods', sa.JSON(), nullable=True),
        sa.Column('preferred_foods', sa.JSON(), nullable=True),
        sa.Column('avg_compliance', sa.Float(), server_default='0'),
        sa.Column('avg_calories_consumed', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_nutrition_weekly_plans_user_week', 'nutrition_weekly_plans', ['user_id', 'year', 'week_number'])

    # UserPreferencesModel
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        # Training
        sa.Column('preferred_training_days', sa.JSON(), nullable=True),
        sa.Column('preferred_training_time', sa.String(20), nullable=True),
        sa.Column('session_duration_minutes', sa.Integer(), server_default='60'),
        sa.Column('equipment_available', sa.JSON(), nullable=True),
        sa.Column('training_location', sa.String(50), nullable=True),
        # Nutrition
        sa.Column('diet_type', sa.String(50), nullable=True),
        sa.Column('allergies', sa.JSON(), nullable=True),
        sa.Column('disliked_foods', sa.JSON(), nullable=True),
        sa.Column('favorite_foods', sa.JSON(), nullable=True),
        sa.Column('meals_per_day', sa.Integer(), server_default='4'),
        sa.Column('cooking_skill', sa.String(20), nullable=True),
        sa.Column('meal_prep_time_minutes', sa.Integer(), server_default='30'),
        # Medical
        sa.Column('pain_tracking_frequency', sa.String(20), server_default='daily'),
        sa.Column('mobility_routine_time', sa.String(20), nullable=True),
        # Notifications
        sa.Column('workout_reminders', sa.Boolean(), server_default='true'),
        sa.Column('meal_reminders', sa.Boolean(), server_default='true'),
        sa.Column('pain_checkin_reminders', sa.Boolean(), server_default='true'),
        sa.Column('reminder_time', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('user_preferences')
    op.drop_index('ix_nutrition_weekly_plans_user_week')
    op.drop_table('nutrition_weekly_plans')
    op.drop_index('ix_coach_weekly_plans_user_week')
    op.drop_table('coach_weekly_plans')
    op.drop_index('ix_medical_protocols_user_week')
    op.drop_table('medical_protocols')
    op.drop_index('ix_weekly_plans_user_week')
    op.drop_table('weekly_plans')
