"""
Test suite for Stripe keys validation with feature flag.
Ensures production security while allowing staging flexibility.
"""

import pytest
import os
from unittest.mock import patch
from app.core.config import Settings


class TestStripeValidation:
    """Test Stripe keys validation logic with ALLOW_STRIPE_TEST_KEYS feature flag."""
    
    def test_production_rejects_test_secret_key(self, monkeypatch):
        """Production mode should reject Stripe test secret keys when flag is False."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)  # Valid secret
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        with pytest.raises(ValueError, match="LIVE Stripe secret key"):
            Settings(
                ALLOW_STRIPE_TEST_KEYS=False,
                STRIPE_SECRET_KEY="sk_test_123456",
                STRIPE_PUBLISHABLE_KEY="pk_live_123456",
                STRIPE_WEBHOOK_SECRET="whsec_123456",
            )
    
    def test_production_rejects_test_publishable_key(self, monkeypatch):
        """Production mode should reject Stripe test publishable keys when flag is False."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        with pytest.raises(ValueError, match="LIVE Stripe publishable key"):
            Settings(
                ALLOW_STRIPE_TEST_KEYS=False,
                STRIPE_SECRET_KEY="sk_live_123456",
                STRIPE_PUBLISHABLE_KEY="pk_test_123456",
                STRIPE_WEBHOOK_SECRET="whsec_123456",
            )
    
    def test_production_requires_secret_key(self, monkeypatch):
        """Production mode requires STRIPE_SECRET_KEY to be set."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        with pytest.raises(ValueError, match="STRIPE_SECRET_KEY must be set"):
            Settings(
                ALLOW_STRIPE_TEST_KEYS=False,
                STRIPE_SECRET_KEY="",
                STRIPE_PUBLISHABLE_KEY="pk_live_123",
                STRIPE_WEBHOOK_SECRET="whsec_123",
            )
    
    def test_production_requires_publishable_key(self, monkeypatch):
        """Production mode requires STRIPE_PUBLISHABLE_KEY to be set."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        with pytest.raises(ValueError, match="STRIPE_PUBLISHABLE_KEY must be set"):
            Settings(
                ALLOW_STRIPE_TEST_KEYS=False,
                STRIPE_SECRET_KEY="sk_live_123",
                STRIPE_PUBLISHABLE_KEY="",
                STRIPE_WEBHOOK_SECRET="whsec_123",
            )
    
    def test_production_requires_webhook_secret(self, monkeypatch):
        """Production mode requires STRIPE_WEBHOOK_SECRET to be set."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        with pytest.raises(ValueError, match="STRIPE_WEBHOOK_SECRET must be set"):
            Settings(
                ALLOW_STRIPE_TEST_KEYS=False,
                STRIPE_SECRET_KEY="sk_live_123",
                STRIPE_PUBLISHABLE_KEY="pk_live_123",
                STRIPE_WEBHOOK_SECRET="",
            )
    
    def test_staging_allows_test_keys_with_flag(self, monkeypatch, caplog):
        """Staging can use test keys with ALLOW_STRIPE_TEST_KEYS=True."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        config = Settings(
            ALLOW_STRIPE_TEST_KEYS=True,
            STRIPE_SECRET_KEY="sk_test_123456",
            STRIPE_PUBLISHABLE_KEY="pk_test_123456",
            STRIPE_WEBHOOK_SECRET="whsec_test_123456",
        )
        
        assert config.STRIPE_SECRET_KEY == "sk_test_123456"
        assert config.STRIPE_PUBLISHABLE_KEY == "pk_test_123456"
        assert config.ALLOW_STRIPE_TEST_KEYS is True
        
        # Check warning logs
        assert "SECURITY WARNING" in caplog.text
        assert "staging" in caplog.text.lower() or "test" in caplog.text.lower()
    
    def test_production_accepts_live_keys(self, monkeypatch):
        """Production accepts live Stripe keys when flag is False."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        config = Settings(
            ALLOW_STRIPE_TEST_KEYS=False,
            STRIPE_SECRET_KEY="sk_live_123456",
            STRIPE_PUBLISHABLE_KEY="pk_live_123456",
            STRIPE_WEBHOOK_SECRET="whsec_123456",
        )
        
        assert config.STRIPE_SECRET_KEY == "sk_live_123456"
        assert config.STRIPE_PUBLISHABLE_KEY == "pk_live_123456"
        assert config.ALLOW_STRIPE_TEST_KEYS is False
    
    def test_development_allows_test_keys_without_flag(self, monkeypatch):
        """Development mode allows test keys without feature flag."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        config = Settings(
            ALLOW_STRIPE_TEST_KEYS=False,  # Flag ignored in dev
            STRIPE_SECRET_KEY="sk_test_123456",
            STRIPE_PUBLISHABLE_KEY="pk_test_123456",
            STRIPE_WEBHOOK_SECRET="whsec_test_123",
        )
        
        assert config.STRIPE_SECRET_KEY == "sk_test_123456"
        assert config.STRIPE_PUBLISHABLE_KEY == "pk_test_123456"
    
    def test_feature_flag_defaults_to_false(self, monkeypatch):
        """ALLOW_STRIPE_TEST_KEYS should default to False for security."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        
        config = Settings(
            STRIPE_SECRET_KEY="sk_test_123",
            STRIPE_PUBLISHABLE_KEY="pk_test_123",
        )
        
        assert config.ALLOW_STRIPE_TEST_KEYS is False
    
    def test_staging_with_live_keys_and_flag(self, monkeypatch, caplog):
        """Staging can use live keys even with flag enabled (flexibility)."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("DB_PASSWORD", "secure_password")
        
        config = Settings(
            ALLOW_STRIPE_TEST_KEYS=True,
            STRIPE_SECRET_KEY="sk_live_123456",
            STRIPE_PUBLISHABLE_KEY="pk_live_123456",
            STRIPE_WEBHOOK_SECRET="whsec_123456",
        )
        
        assert config.STRIPE_SECRET_KEY == "sk_live_123456"
        assert "LIVE secret key" in caplog.text
