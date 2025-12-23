"""Portfolio & File Upload Constants"""

from typing import Final


class PortfolioConstants:
    """Portfolio-related constants."""

    # Slug
    SLUG_MIN_LENGTH: Final[int] = 3
    SLUG_MAX_LENGTH: Final[int] = 50
    SLUG_PATTERN: Final[str] = r"^[a-z0-9-]+$"

    # Skill levels
    SKILL_LEVEL_MIN: Final[int] = 1
    SKILL_LEVEL_MAX: Final[int] = 5
    SKILL_LEVEL_BEGINNER: Final[int] = 1
    SKILL_LEVEL_INTERMEDIATE: Final[int] = 3
    SKILL_LEVEL_ADVANCED: Final[int] = 4
    SKILL_LEVEL_EXPERT: Final[int] = 5

    # Project URL
    PROJECT_URL_MAX_LENGTH: Final[int] = 2048

    # Experience/Education
    MAX_DESCRIPTION_LENGTH: Final[int] = 5000
    MAX_TITLE_LENGTH: Final[int] = 200
    MAX_COMPANY_LENGTH: Final[int] = 200

    # Profile
    MAX_BIO_LENGTH: Final[int] = 1000
    MAX_HEADLINE_LENGTH: Final[int] = 200
    MAX_LOCATION_LENGTH: Final[int] = 100

    # Social links
    MAX_SOCIAL_LINKS: Final[int] = 10
    MAX_SOCIAL_URL_LENGTH: Final[int] = 500


class FileUploadConstants:
    """File upload limits and allowed types."""

    # File size limits (bytes)
    MAX_AVATAR_SIZE_MB: Final[int] = 2
    MAX_AVATAR_SIZE_BYTES: Final[int] = MAX_AVATAR_SIZE_MB * 1024 * 1024
    MAX_CV_SIZE_MB: Final[int] = 5
    MAX_CV_SIZE_BYTES: Final[int] = MAX_CV_SIZE_MB * 1024 * 1024
    MAX_PROJECT_IMAGE_SIZE_MB: Final[int] = 5
    MAX_PROJECT_IMAGE_SIZE_BYTES: Final[int] = MAX_PROJECT_IMAGE_SIZE_MB * 1024 * 1024

    # Allowed file types
    ALLOWED_IMAGE_TYPES: Final[list] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_CV_TYPES: Final[list] = ["application/pdf"]
    ALLOWED_AVATAR_EXTENSIONS: Final[list] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_CV_EXTENSIONS: Final[list] = [".pdf"]

    # Image dimensions
    MAX_IMAGE_WIDTH: Final[int] = 4096
    MAX_IMAGE_HEIGHT: Final[int] = 4096
    AVATAR_SIZE: Final[int] = 256
    THUMBNAIL_SIZE: Final[int] = 150
