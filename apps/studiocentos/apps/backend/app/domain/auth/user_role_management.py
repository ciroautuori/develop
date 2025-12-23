"""User Role Management Service
Handles role downgrades and subscription expiration logic.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.domain.auth.models import User, UserRole
# Profile model removed - merged into UserVisibility
from app.domain.portfolio.services.profile_service import ProfileService

logger = logging.getLogger(__name__)

class UserRoleManagementService:
    """Service for managing user role transitions and subscription expiration."""

    def __init__(self):
        self.profile_service = ProfileService()

    def expire_trial_users(self, db: Session) -> int:
        """Convert expired trial users to regular users and block their profiles.

        Args:
            db: Database session

        Returns:
            Number of users processed
        """
        now = datetime.now(timezone.utc)

        # Find expired trial users
        expired_trials = (
            db.query(User)
            .filter(
                and_(
                    User.role == UserRole.TRIAL,
                    User.trial_expires_at.isnot(None),
                    User.trial_expires_at <= now,
                )
            )
            .all()
        )

        processed_count = 0

        for user in expired_trials:
            # Downgrade role
            user.role = UserRole.USER

            # Block user's profile if exists
            if user.user:
                user.user.visibility = ProfileVisibility.BLOCKED
                user.user.blocked_reason = (
                    "Trial period expired - upgrade required for public portfolio"
                )
                user.user.blocked_at = now
                user.user.is_public = False

            db.add(user)
            processed_count += 1

        db.commit()
        logger.info(f"Processed {processed_count} expired trial users")
        return processed_count

    def downgrade_subscription_expired_users(self, db: Session) -> int:
        """Downgrade users whose subscriptions have expired to customer role.
        Block their profiles according to business rules.

        Args:
            db: Database session

        Returns:
            Number of users processed
        """
        # Placeholder: In real implementation, check subscription table
        # For now, we'll implement the core logic for when subscription system is ready

        datetime.now(timezone.utc)
        processed_count = 0

        # Example logic for when subscription system exists:
        # expired_pro_users = db.query(User).join(Subscription).filter(
        #     User.role == UserRole.PRO,
        #     Subscription.expires_at <= now,
        #     Subscription.is_active == True
        # ).all()

        # For now, we simulate the downgrade logic
        # This will be activated when subscription system is implemented

        logger.info(f"Processed {processed_count} subscription expired users (placeholder)")
        return processed_count

    def block_customer_profiles(self, db: Session) -> int:
        """Block all customer profiles as per business requirement.
        Customer profiles should not be public unless they have active subscription.

        Args:
            db: Database session

        Returns:
            Number of profiles blocked
        """
        now = datetime.now(timezone.utc)

        # Find all customer profiles that are not blocked
        customer_profiles = (
            db.query(User)
            .join(User)
            .filter(User.role == UserRole.CUSTOMER.visibility != ProfileVisibility.BLOCKED)
            .all()
        )

        blocked_count = 0

        for profile in customer_profiles:
            profile.visibility = ProfileVisibility.BLOCKED
            profile.blocked_reason = "Customer subscription required for public portfolio"
            profile.blocked_at = now
            profile.is_public = False

            db.add(profile)
            blocked_count += 1

        db.commit()
        logger.info(f"Blocked {blocked_count} customer profiles")
        return blocked_count

    def unblock_user_profile_on_upgrade(
        self, db: Session, user_id: int, new_role: UserRole
    ) -> bool:
        """Unblock user profile when they upgrade their subscription.

        Args:
            db: Database session
            user_id: User ID
            new_role: New user role

        Returns:
            True if profile was unblocked, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.user:
            return False

        # Check if new role allows public portfolios
        if new_role in [UserRole.TRIAL, UserRole.PRO, UserRole.TESTER]:
            # Unblock profile
            user.role = new_role
            user.user.visibility = ProfileVisibility.PUBLIC
            user.user.blocked_reason = None
            user.user.blocked_at = None
            user.user.is_public = True

            db.add(user)
            db.commit()

            logger.info(f"Unblocked profile for user {user_id} on upgrade to {new_role.value}")
            return True

        return False

    def process_role_transitions(self, db: Session) -> dict:
        """Process all role transitions and profile updates.
        This method should be called by scheduled jobs.

        Args:
            db: Database session

        Returns:
            Summary of operations performed
        """
        results = {
            "expired_trials": 0,
            "expired_subscriptions": 0,
            "blocked_customer_profiles": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Process expired trials
            results["expired_trials"] = self.expire_trial_users(db)

            # Process expired subscriptions
            results["expired_subscriptions"] = self.downgrade_subscription_expired_users(db)

            # Block customer profiles
            results["blocked_customer_profiles"] = self.block_customer_profiles(db)

            logger.info(f"Role transition processing completed: {results}")

        except Exception as e:
            logger.error(f"Error during role transition processing: {str(e)}")
            raise

        return results

    def get_users_by_role_status(self, db: Session) -> dict:
        """Get statistics of users by role and profile status.

        Args:
            db: Database session

        Returns:
            Dictionary with user statistics
        """
        stats = {}

        for role in UserRole:
            role_users = db.query(User).filter(User.role == role).count()

            # Count blocked profiles for this role
            blocked_profiles = (
                db.query(User)
                .join(User)
                .filter(User.role == role.visibility == ProfileVisibility.BLOCKED)
                .count()
            )

            # Count public profiles for this role
            public_profiles = (
                db.query(User)
                .join(User)
                .filter(User.role == role.visibility == ProfileVisibility.PUBLIC)
                .count()
            )

            stats[role.value] = {
                "total_users": role_users,
                "blocked_profiles": blocked_profiles,
                "public_profiles": public_profiles,
                "private_profiles": role_users - blocked_profiles - public_profiles,
            }

        return stats
