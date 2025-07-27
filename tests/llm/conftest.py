"""
LLM-specific test fixtures and configuration.

This module provides fixtures specifically for testing LLM functionality,
including mock services, test data, and configuration helpers.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml

from app.llm.config import LLMConfig
from app.llm.services import LLMService


@pytest.fixture
def llm_config_data():
    """Load test LLM configuration data."""
    # Get project root directory (3 levels up from this file)
    config_path = Path(__file__).parent.parent.parent / "llm_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def test_models_list(llm_config_data):
    """Extract testing models from config."""
    testing_models = {}
    for task_name, task_config in llm_config_data.get("tasks", {}).items():
        testing_models[task_name] = task_config.get("testing", [])
    return testing_models


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing without real API calls."""
    service = MagicMock(spec=LLMService)

    # Mock async methods
    service.generate_story = AsyncMock(
        return_value={
            "story": "Once upon a time, in a land far away...",
            "metadata": {
                "model": "test-model",
                "tokens_used": 150,
                "generation_time": 2.5,
                "temperature": 0.7,
            },
        }
    )

    service.analyze_story = AsyncMock(
        return_value={
            "analysis": "This is a fantasy story with positive sentiment.",
            "analysis_type": "full",
            "metadata": {
                "model": "test-model",
                "confidence": 0.85,
                "processing_time": 1.2,
            },
        }
    )

    service.summarize_story = AsyncMock(
        return_value={
            "summary": "A brief summary of the story content.",
            "metadata": {
                "model": "test-model",
                "original_length": 500,
                "summary_length": 50,
                "compression_ratio": 0.1,
            },
        }
    )

    service.improve_story = AsyncMock(
        return_value={
            "improved_story": "An improved version of the story.",
            "original_story": "Original story content.",
            "metadata": {
                "model": "test-model",
                "improvement_type": "general",
                "changes_made": 15,
            },
        }
    )

    service.get_available_models = MagicMock(
        return_value={
            "gpt-4.1-mini": True,
            "gpt-4.1-nano": True,
            "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": False,
            "google/gemma-3-4b-it": True,
        }
    )

    service.get_usage_stats = MagicMock(
        return_value={
            "requests_count": 42,
            "total_tokens": 12500,
            "errors_count": 2,
            "last_request": "2025-07-18T10:30:00",
            "average_response_time": 2.1,
        }
    )

    return service


@pytest.fixture
def sample_story_content():
    """Sample story content for testing."""
    return """
    In the mystical forest of Eldoria, where ancient trees whispered secrets 
    to those who knew how to listen, a young adventurer named Luna discovered 
    a hidden path that would change her destiny forever. The moonlight filtered 
    through the canopy above, casting ethereal shadows that danced on the forest floor.
    
    As she ventured deeper into the woods, Luna heard the gentle sound of flowing 
    water. Following the melodic stream, she stumbled upon a clearing where a 
    magnificent crystal fountain stood, its waters glowing with an otherworldly light.
    
    Little did she know that this fountain was the source of all magic in the realm,
    and that her discovery would set in motion events that would either save 
    the kingdom or doom it to eternal darkness.
    """


@pytest.fixture
def sample_generation_requests():
    """Sample requests for story generation testing."""
    return [
        {
            "prompt": "A brave knight on a quest",
            "genre": "fantasy",
            "length": "short",
            "style": "heroic",
        },
        {
            "prompt": "A detective solving a mystery",
            "genre": "mystery",
            "length": "medium",
            "style": "noir",
        },
        {
            "prompt": "A love story in space",
            "genre": "science fiction",
            "length": "long",
            "style": "romantic",
        },
    ]


@pytest.fixture
def sample_analysis_requests(sample_story_content):
    """Sample requests for story analysis testing."""
    return [
        {"content": sample_story_content, "analysis_type": "sentiment"},
        {"content": sample_story_content, "analysis_type": "genre"},
        {"content": sample_story_content, "analysis_type": "full"},
    ]


@pytest.fixture
def sample_summary_requests(sample_story_content):
    """Sample requests for story summarization testing."""
    return [
        {
            "content": sample_story_content,
            "summary_length": "brief",
            "focus": "main plot",
        },
        {
            "content": sample_story_content,
            "summary_length": "detailed",
            "focus": "characters and setting",
        },
    ]


@pytest.fixture
def sample_improvement_requests(sample_story_content):
    """Sample requests for story improvement testing."""
    return [
        {
            "content": sample_story_content,
            "improvement_type": "general",
            "focus_area": "overall quality",
            "target_audience": "young adults",
        },
        {
            "content": sample_story_content,
            "improvement_type": "grammar",
            "focus_area": "punctuation and structure",
            "target_audience": "general readers",
        },
        {
            "content": sample_story_content,
            "improvement_type": "style",
            "focus_area": "narrative voice",
            "target_audience": "literary fiction readers",
            "target_style": "minimalist",
        },
    ]


@pytest.fixture
def skip_llm_integration_tests(llm_config_data):
    """Determine whether to skip integration tests based on available providers and API keys."""
    import os

    # Skip if explicitly disabled
    skip_integration = (
        os.getenv("SKIP_LLM_INTEGRATION_TESTS", "false").lower() == "true"
    )
    if skip_integration:
        pytest.skip(
            "Skipping LLM integration tests: integration tests explicitly disabled."
        )

    # Extract required API keys from config
    providers_config = llm_config_data.get("providers", {})
    required_api_keys = []
    available_providers = []

    for provider_name, provider_config in providers_config.items():
        if provider_config.get("requires_api_key", False):
            api_key_env = provider_config.get("api_key_env")
            if api_key_env:
                required_api_keys.append(api_key_env)
                if os.getenv(api_key_env):
                    available_providers.append(provider_name)

    # Check if at least one provider has an API key available
    if not available_providers:
        missing_keys = [key for key in required_api_keys if not os.getenv(key)]
        pytest.skip(
            f"Skipping LLM integration tests. No API keys available for configured providers. Missing: {missing_keys}"
        )

    return True


def pytest_configure(config):
    """Configure pytest markers for LLM tests."""
    config.addinivalue_line(
        "markers", "llm_integration: mark test as LLM integration test"
    )
    config.addinivalue_line("markers", "llm_mock: mark test as LLM mock test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
