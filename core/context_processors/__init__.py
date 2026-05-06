# core/context_processors/__init__.py
from .app_processor import app_settings
from .tenant_processor import tenant_context

__all__ = ["app_settings", "tenant_context"]
