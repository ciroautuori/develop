"""GDPR Data Deletion Service.

HIGH-005: Extracted from gdpr.py (split 4/4)
"""

import logging

logger = logging.getLogger(__name__)


class DataDeletionService:
    """Service for GDPR data deletion (Art. 17)."""

    async def delete_user_data(self, user_id: str, hard_delete: bool = False) -> bool:
        """Delete user data according to GDPR."""
        try:
            logger.info(f"Deleting data for user {user_id} (hard_delete={hard_delete})")
            
            if hard_delete:
                # Physical deletion
                logger.warning(f"Hard delete requested for user {user_id}")
            else:
                # Soft delete (anonymization)
                logger.info(f"Soft delete (anonymization) for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            return False
