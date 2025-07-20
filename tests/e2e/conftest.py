"""
E2E test fixtures and configuration.

This module provides fixtures for end-to-end testing,
combining story management and LLM functionality.
"""

import pytest
import yaml


@pytest.fixture
def llm_config_data():
    """Load test LLM configuration data."""
    config_path = "/home/livierek/projekty/story-teller/llm_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def test_models_list(llm_config_data):
    """Extract testing models from config."""
    testing_models = {}
    for task_name, task_config in llm_config_data.get('tasks', {}).items():
        testing_models[task_name] = task_config.get('testing', [])
    return testing_models


@pytest.fixture
def integration_test_models(test_models_list):
    """Get models available for integration testing - imported from LLM conftest."""
    # Filter out models that are expensive or slow for testing
    fast_models = [
        "gpt-4.1-nano",
        "google/gemma-3-4b-it"
    ]
    
    available_models = {}
    for task, models in test_models_list.items():
        # Only include fast models for testing
        available_models[task] = [m for m in models if m in fast_models]
    
    return available_models


@pytest.fixture
def skip_integration_tests():
    """Skip LLM integration tests if required environment variables are not set."""
    import os
    
    required_env_vars = [
        "OPENAI_API_KEY",
        "GROQ_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Skipping LLM integration tests. Missing environment variables: {missing_vars}")
    
    return True
