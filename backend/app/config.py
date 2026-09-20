"""
AEGIS INVEST — Central Configuration Access Point
Re-exports application configuration settings for canonical root-level app import.
"""

from app.core.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
