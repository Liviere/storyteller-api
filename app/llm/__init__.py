"""
LLM Module for Story Teller API

This module provides Large Language Model capabilities for:
- Story generation
- Content analysis and categorization
- Sentiment analysis
- Text transformation and improvement
- Multilingual support

The module is designed to work with OpenAI-compatible models
"""

# Import will be available after installing dependencies
try:
    from .config import LLMConfig, llm_config
    from .models import LLMModelFactory, get_model_factory
    from .services import LLMService, get_llm_service

    __all__ = [
        "LLMService",
        "get_llm_service",
        "LLMModelFactory",
        "get_model_factory",
        "LLMConfig",
        "llm_config",
    ]
except ImportError:
    # LangChain dependencies not yet installed
    __all__ = []
