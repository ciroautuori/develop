"""
Test suite for authentication service.
Covers password hashing, user registration, and login validation.
"""

import pytest
from app.domain.auth.services import AuthService
from app.domain.auth.models import User, UserRole
from app.domain.auth.repositories.user_repository import UserRepository


class TestAuthServicePasswordManagement:
    """Test password hashing and validation."""
    
    def test_password_hashing_is_secure(self, auth_service):
        """Password should be hashed with bcrypt."""
        plain_password = "MySecretPassword123"
        hashed = auth_service.get_password_hash(plain_password)
        
        # Hash should be different from plain
        assert hashed != plain_password
        # Should be bcrypt format
        assert hashed.startswith("$2b$")
        # Should have minimum length
        assert len(hashed) > 50
    
    def test_verify_password_works(self, auth_service):
        """Password verification should work correctly."""
        plain_password = "TestPassword123"
        hashed = auth_service.get_password_hash(plain_password)
        
        # Correct password should verify
        assert auth_service.verify_password(plain_password, hashed) is True
        
        # Wrong password should not verify
        assert auth_service.verify_password("WrongPassword", hashed) is False
    
    def test_password_strength_validation(self, auth_service):
        """Weak passwords should be rejected."""
        # Too short
        assert auth_service.validate_password_strength("short") is False
        
        # No digits
        assert auth_service.validate_password_strength("nodigitspassword") is False
        
        # Valid password
        assert auth_service.validate_password_strength("GoodPass123") is True
        assert auth_service.validate_password_strength("SecurePassword999!") is True
    
    def test_different_passwords_produce_different_hashes(self, auth_service):
        """Same password should produce different hashes (salt)."""
        password = "SamePassword123"
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify the password
        assert auth_service.verify_password(password, hash1) is True
        assert auth_service.verify_password(password, hash2) is True


@pytest.fixture
def auth_service(db_session):
    """Create AuthService instance with test database."""
    repository = UserRepository(db_session)
    return AuthService(repository)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    }
