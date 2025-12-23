"""Add extended user profile fields for comprehensive wizard data

Revision ID: 009
Revises: 008_add_weekly_plans_tables
Create Date: 2025-01-22 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = 'wizard_sessions_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add extended user profile fields for:
    - Training goals & experience
    - Lifestyle & recovery
    - Nutrition goals & preferences
    - Allergies & dietary restrictions
    """

    # =========================================================================
    # TRAINING GOALS & EXPERIENCE
    # =========================================================================

    # Training experience level
    op.add_column('users', sa.Column(
        'training_experience',
        sa.String(50),
        nullable=True,
        comment='beginner, intermediate, advanced, elite'
    ))

    op.add_column('users', sa.Column(
        'training_years',
        sa.Integer,
        nullable=True,
        comment='Years of training experience'
    ))

    # Secondary goals (JSON array)
    op.add_column('users', sa.Column(
        'secondary_goals',
        postgresql.JSONB,
        nullable=True,
        comment='List of secondary training goals'
    ))

    # Available training days per week
    op.add_column('users', sa.Column(
        'available_days',
        sa.Integer,
        nullable=True,
        comment='Days per week available for training'
    ))

    # Preferred training time
    op.add_column('users', sa.Column(
        'preferred_time',
        sa.String(50),
        nullable=True,
        comment='morning, afternoon, evening, flexible'
    ))

    # Intensity preference
    op.add_column('users', sa.Column(
        'intensity_preference',
        sa.String(50),
        nullable=True,
        comment='low, moderate, high, variable'
    ))

    # =========================================================================
    # LIFESTYLE & RECOVERY
    # =========================================================================

    # Activity level (already exists conceptually, add TDEE context)
    op.add_column('users', sa.Column(
        'activity_level',
        sa.String(50),
        nullable=True,
        comment='sedentary, lightly_active, moderately_active, very_active, extra_active'
    ))

    op.add_column('users', sa.Column(
        'work_type',
        sa.String(50),
        nullable=True,
        comment='desk_job, light_activity, moderate_activity, heavy_labor, mixed'
    ))

    op.add_column('users', sa.Column(
        'work_hours_per_day',
        sa.Integer,
        nullable=True,
        comment='Hours worked per day'
    ))

    op.add_column('users', sa.Column(
        'commute_active',
        sa.Boolean,
        nullable=True,
        server_default='false',
        comment='Whether commute involves walking/cycling'
    ))

    op.add_column('users', sa.Column(
        'stress_level',
        sa.Integer,
        nullable=True,
        comment='1-5 stress scale'
    ))

    op.add_column('users', sa.Column(
        'stress_sources',
        postgresql.JSONB,
        nullable=True,
        comment='List of stress sources'
    ))

    op.add_column('users', sa.Column(
        'sleep_hours',
        sa.Float,
        nullable=True,
        comment='Average hours of sleep'
    ))

    op.add_column('users', sa.Column(
        'sleep_quality',
        sa.String(50),
        nullable=True,
        comment='poor, fair, good, excellent'
    ))

    op.add_column('users', sa.Column(
        'sleep_schedule',
        sa.String(50),
        nullable=True,
        comment='consistent, variable, shift_work, irregular'
    ))

    op.add_column('users', sa.Column(
        'recovery_capacity',
        sa.String(50),
        nullable=True,
        comment='fast, normal, slow, variable'
    ))

    op.add_column('users', sa.Column(
        'health_conditions',
        postgresql.JSONB,
        nullable=True,
        comment='List of health conditions'
    ))

    op.add_column('users', sa.Column(
        'supplements_used',
        postgresql.JSONB,
        nullable=True,
        comment='List of supplements currently used'
    ))

    # =========================================================================
    # NUTRITION GOALS & PREFERENCES
    # =========================================================================

    op.add_column('users', sa.Column(
        'nutrition_goal',
        sa.String(50),
        nullable=True,
        comment='fat_loss, muscle_gain, maintenance, recomp, performance'
    ))

    op.add_column('users', sa.Column(
        'diet_type',
        sa.String(50),
        nullable=True,
        comment='balanced, low_carb, keto, high_protein, mediterranean, vegetarian, vegan, pescatarian'
    ))

    op.add_column('users', sa.Column(
        'calorie_preference',
        sa.String(50),
        nullable=True,
        comment='auto_calculate, manual'
    ))

    op.add_column('users', sa.Column(
        'custom_calories',
        sa.Integer,
        nullable=True,
        comment='Custom daily calorie target'
    ))

    op.add_column('users', sa.Column(
        'protein_priority',
        sa.String(50),
        nullable=True,
        comment='standard, high, very_high'
    ))

    op.add_column('users', sa.Column(
        'macro_preference',
        sa.String(50),
        nullable=True,
        comment='balanced, high_protein, low_carb, high_carb, flexible'
    ))

    op.add_column('users', sa.Column(
        'meal_frequency',
        sa.Integer,
        nullable=True,
        comment='Number of meals per day'
    ))

    op.add_column('users', sa.Column(
        'meal_timing',
        sa.String(50),
        nullable=True,
        comment='flexible, structured, intermittent_fasting, pre_post_workout'
    ))

    op.add_column('users', sa.Column(
        'intermittent_window',
        sa.String(50),
        nullable=True,
        comment='16:8, 18:6, 20:4, 5:2, custom'
    ))

    op.add_column('users', sa.Column(
        'budget_preference',
        sa.String(50),
        nullable=True,
        comment='budget_friendly, moderate, premium, no_limit'
    ))

    op.add_column('users', sa.Column(
        'cooking_skill',
        sa.String(50),
        nullable=True,
        comment='beginner, intermediate, advanced, chef'
    ))

    op.add_column('users', sa.Column(
        'meal_prep_available',
        sa.Boolean,
        nullable=True,
        server_default='true',
        comment='Whether user can meal prep'
    ))

    op.add_column('users', sa.Column(
        'supplements_interest',
        postgresql.JSONB,
        nullable=True,
        comment='List of supplements user is interested in'
    ))

    # =========================================================================
    # ALLERGIES & DIETARY RESTRICTIONS
    # =========================================================================

    op.add_column('users', sa.Column(
        'allergies',
        postgresql.JSONB,
        nullable=True,
        comment='Food allergies (e.g., peanuts, tree_nuts, shellfish)'
    ))

    op.add_column('users', sa.Column(
        'intolerances',
        postgresql.JSONB,
        nullable=True,
        comment='Food intolerances (e.g., lactose, gluten)'
    ))

    op.add_column('users', sa.Column(
        'dietary_restrictions',
        postgresql.JSONB,
        nullable=True,
        comment='Dietary restrictions (e.g., no_pork, no_beef, halal, kosher)'
    ))

    # =========================================================================
    # FAVORITE/DISLIKED FOODS
    # =========================================================================

    op.add_column('users', sa.Column(
        'favorite_foods',
        postgresql.JSONB,
        nullable=True,
        comment='List of favorite foods'
    ))

    op.add_column('users', sa.Column(
        'disliked_foods',
        postgresql.JSONB,
        nullable=True,
        comment='List of disliked foods'
    ))


def downgrade() -> None:
    """Remove all extended user profile fields."""

    # Favorite/Disliked foods
    op.drop_column('users', 'favorite_foods')
    op.drop_column('users', 'disliked_foods')

    # Allergies & restrictions
    op.drop_column('users', 'allergies')
    op.drop_column('users', 'intolerances')
    op.drop_column('users', 'dietary_restrictions')

    # Nutrition preferences
    op.drop_column('users', 'nutrition_goal')
    op.drop_column('users', 'diet_type')
    op.drop_column('users', 'calorie_preference')
    op.drop_column('users', 'custom_calories')
    op.drop_column('users', 'protein_priority')
    op.drop_column('users', 'macro_preference')
    op.drop_column('users', 'meal_frequency')
    op.drop_column('users', 'meal_timing')
    op.drop_column('users', 'intermittent_window')
    op.drop_column('users', 'budget_preference')
    op.drop_column('users', 'cooking_skill')
    op.drop_column('users', 'meal_prep_available')
    op.drop_column('users', 'supplements_interest')

    # Lifestyle & recovery
    op.drop_column('users', 'activity_level')
    op.drop_column('users', 'work_type')
    op.drop_column('users', 'work_hours_per_day')
    op.drop_column('users', 'commute_active')
    op.drop_column('users', 'stress_level')
    op.drop_column('users', 'stress_sources')
    op.drop_column('users', 'sleep_hours')
    op.drop_column('users', 'sleep_quality')
    op.drop_column('users', 'sleep_schedule')
    op.drop_column('users', 'recovery_capacity')
    op.drop_column('users', 'health_conditions')
    op.drop_column('users', 'supplements_used')

    # Training goals
    op.drop_column('users', 'training_experience')
    op.drop_column('users', 'training_years')
    op.drop_column('users', 'secondary_goals')
    op.drop_column('users', 'available_days')
    op.drop_column('users', 'preferred_time')
    op.drop_column('users', 'intensity_preference')
