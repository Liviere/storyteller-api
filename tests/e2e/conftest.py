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
def skip_integration_tests(llm_config_data):
    """Skip LLM integration tests if no API keys for configured providers are available."""
    import os
    
    # Skip if explicitly disabled
    skip_integration = os.getenv("SKIP_LLM_INTEGRATION_TESTS", "false").lower() == "true"
    if skip_integration:
        pytest.skip("Skipping LLM integration tests: integration tests explicitly disabled.")
    
    # Extract required API keys from config
    providers_config = llm_config_data.get('providers', {})
    required_api_keys = []
    available_providers = []
    
    for provider_name, provider_config in providers_config.items():
        if provider_config.get('requires_api_key', False):
            api_key_env = provider_config.get('api_key_env')
            if api_key_env:
                required_api_keys.append(api_key_env)
                if os.getenv(api_key_env):
                    available_providers.append(provider_name)
    
    # Check if at least one provider has an API key available
    if not available_providers:
        missing_keys = [key for key in required_api_keys if not os.getenv(key)]
        pytest.skip(f"Skipping LLM integration tests. No API keys available for configured providers. Missing: {missing_keys}")
    
    return True
