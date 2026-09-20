"""
AEGIS INVEST — Centralized Application Configuration
Provides strongly typed, validated settings using Pydantic Settings.
Loaded from environment variables with graceful defaults.
"""

from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    AEGIS Platform Configuration Settings.
    Strictly parses and validates environment settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --------------------------------------------------------------------------
    # Application Metadata
    # --------------------------------------------------------------------------
    app_name: str = Field(default="aegis-invest", description="Application service name")
    app_env: str = Field(default="development", description="Environment: development, staging, production, testing")
    app_version: str = Field(default="0.1.0", description="Semantic version of application")
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # --------------------------------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------------------------------
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    log_format: str = Field(default="console", description="Format: console (human-readable) or json (production)")

    # --------------------------------------------------------------------------
    # API Server Configuration
    # --------------------------------------------------------------------------
    api_host: str = Field(default="0.0.0.0", description="API server host interface")
    api_port: int = Field(default=8000, description="API server port")
    api_v1_prefix: str = Field(default="/api/v1", description="Prefix for API v1 routes")
    allowed_hosts: str = Field(default="*", description="Allowed hosts for TrustedHost middleware")

    # --------------------------------------------------------------------------
    # Security & CORS
    # --------------------------------------------------------------------------
    secret_key: str = Field(
        default="local-development-only-secret-key-do-not-use-in-production-aegis",
        description="Application secret key used for cryptographic signing",
    )
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins",
    )
    rate_limit_per_minute: int = Field(default=120, description="Rate limit per IP per minute")

    # --------------------------------------------------------------------------
    # Database (PostgreSQL / SQLite fallback for testing)
    # --------------------------------------------------------------------------
    database_url: str = Field(
        default="sqlite+aiosqlite:///./aegis_local.db",
        description="Async database connection string",
    )
    database_pool_size: int = Field(default=5, description="Connection pool size")
    database_max_overflow: int = Field(default=10, description="Connection pool max overflow")
    database_pool_timeout: int = Field(default=30, description="Pool checkout timeout in seconds")
    database_echo: bool = Field(default=False, description="Echo SQL queries to log (debug only)")

    # --------------------------------------------------------------------------
    # Caching & Infrastructure (Redis)
    # --------------------------------------------------------------------------
    redis_enabled: bool = Field(default=False, description="Enable Redis cache & message broker")
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        valid_envs = {"development", "staging", "production", "testing"}
        v_clean = v.lower().strip()
        if v_clean not in valid_envs:
            raise ValueError(f"Invalid APP_ENV: '{v}'. Must be one of: {', '.join(valid_envs)}")
        return v_clean

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def parsed_cors_origins(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
