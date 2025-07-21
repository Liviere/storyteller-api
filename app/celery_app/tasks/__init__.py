"""
Celery tasks initialization
"""

from . import stories
from . import llm

__all__ = ["stories", "llm"]
