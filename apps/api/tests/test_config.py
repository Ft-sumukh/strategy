"""
Tests for configuration management and settings validation.
"""

import pytest
from app.core.config import Settings


def test_settings_default_values():
    """Verifies default settings are configured appropriately."""
    settings = Settings(app_name="aegis-test", app_env="development")
    assert settings.app_name == "aegis-test"
    assert settings.app_version == "0.1.0"
    assert settings.is_development is True
    assert settings.is_production is False


def test_settings_invalid_env():
    """Verifies that invalid environment names are rejected with ValueError."""
    with pytest.raises(ValueError, match="Invalid APP_ENV"):
        Settings(app_env="invalid_environment")


def test_cors_origins_parsing():
    """Verifies parsing of comma-separated CORS origins."""
    settings = Settings(cors_origins="https://app.aegis.com, https://admin.aegis.com")
    parsed = settings.parsed_cors_origins
    assert len(parsed) == 2
    assert "https://app.aegis.com" in parsed
    assert "https://admin.aegis.com" in parsed
