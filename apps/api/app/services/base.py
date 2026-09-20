"""
AEGIS INVEST — Service Layer Foundation
Base class for all business logic, orchestration, and domain services.
"""

from app.core.logging import get_logger


class BaseService:
    """Base service class providing logger access and common service lifecycle hooks."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
