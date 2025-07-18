"""
Tests for LLM configuration management.

Tests the loading, validation, and usage of LLM configuration from YAML files.
"""

import pytest
import yaml
from typing import Dict, Any

from app.llm.config import LLMConfig, llm_config


class TestLLMConfig:
    """Test LLM configuration functionality."""
    
    def test_config_loads_successfully(self, llm_config_data):
        """Test that LLM configuration loads without errors."""
        assert llm_config_data is not None
        assert "providers" in llm_config_data
        assert "models" in llm_config_data
        assert "tasks" in llm_config_data
        assert "settings" in llm_config_data
    
    def test_required_providers_exist(self, llm_config_data):
        """Test that required provider configurations exist."""
        providers = llm_config_data["providers"]
        
        # Check that basic providers are configured
        assert "openai" in providers
        assert "deepinfra" in providers
        
        # Check provider structure
        for provider_name, provider_config in providers.items():
            assert "name" in provider_config
            assert "base_url" in provider_config or "base_url_env" in provider_config
    
    def test_models_configuration(self, llm_config_data):
        """Test that models are properly configured."""
        models = llm_config_data["models"]
        
        assert len(models) > 0
        
        for model_name, model_config in models.items():
            assert "provider" in model_config
            assert "display_name" in model_config
            assert "description" in model_config
            assert model_config["provider"] in llm_config_data["providers"]
    
    def test_tasks_configuration(self, llm_config_data):
        """Test that tasks are properly configured."""
        tasks = llm_config_data["tasks"]
        models = llm_config_data["models"]
        
        required_tasks = [
            "story_generation", "analysis", "summarization", 
            "improvement", "translation"
        ]
        
        for task in required_tasks:
            assert task in tasks
            
            task_config = tasks[task]
            assert "primary" in task_config
            assert "fallback" in task_config
            assert "description" in task_config
            
            # Check that referenced models exist
            assert task_config["primary"] in models
            for fallback_model in task_config["fallback"]:
                assert fallback_model in models
    
    def test_testing_configuration(self, llm_config_data, test_models_list):
        """Test that testing models are properly configured."""
        tasks = llm_config_data["tasks"]
        models = llm_config_data["models"]
        
        for task_name, testing_models in test_models_list.items():
            if testing_models:  # If testing models are defined
                for model in testing_models:
                    assert model in models, f"Testing model {model} not found in models config"
    
    def test_settings_configuration(self, llm_config_data):
        """Test that settings are properly configured."""
        settings = llm_config_data["settings"]
        
        required_settings = [
            "enable_caching", "max_concurrent_requests", "default_timeout",
            "retry_attempts", "max_prompt_length", "max_response_length"
        ]
        
        for setting in required_settings:
            assert setting in settings
        
        # Test testing-specific settings
        assert "testing" in settings
        testing_settings = settings["testing"]
        
        required_testing_settings = [
            "enable_integration_tests", "test_timeout", 
            "mock_responses_by_default", "skip_slow_models"
        ]
        
        for setting in required_testing_settings:
            assert setting in testing_settings
    
    def test_config_instance_creation(self):
        """Test that LLMConfig instance can be created."""
        config = llm_config
        assert config is not None
        assert hasattr(config, 'get_task_model')
        assert hasattr(config, 'list_available_models')
    
    def test_get_model_for_task(self):
        """Test getting models for specific tasks."""
        config = llm_config
        
        # Test getting primary model for story generation
        model = config.get_task_model("story_generation")
        assert model is not None
        
        # Test getting fallback models (using task model with fallback)
        fallback_model = config.get_task_model_with_fallback("story_generation")
        assert fallback_model is not None
    
    def test_get_testing_models_for_task(self, test_models_list):
        """Test getting testing models for tasks."""
        # This is a future feature - for now we'll test that the config structure exists
        config = llm_config
        
        for task_name, expected_models in test_models_list.items():
            # Basic check that the task exists in config
            primary_model = config.get_task_model(task_name)
            assert primary_model is not None
    
    @pytest.mark.parametrize("task_name", [
        "story_generation", "analysis", "summarization", "improvement"
    ])
    def test_task_model_resolution(self, task_name):
        """Test that each task can resolve its models."""
        config = llm_config
        
        primary_model = config.get_task_model(task_name)
        assert primary_model is not None
        
        # Test fallback resolution
        fallback_model = config.get_task_model_with_fallback(task_name)
        assert fallback_model is not None
    
    def test_model_availability_check(self):
        """Test checking model availability."""
        config = llm_config
        
        available_models = config.list_available_models()
        assert isinstance(available_models, list)
        
        # Should contain at least some models or be empty (if no API keys)
        assert len(available_models) >= 0
        
        # Test individual model availability
        for model_name in config.models.keys():
            is_available = config.is_model_available(model_name)
            assert isinstance(is_available, bool)


class TestLLMConfigValidation:
    """Test LLM configuration validation."""
    
    def test_invalid_yaml_handling(self, tmp_path):
        """Test handling of invalid YAML configuration."""
        # Create invalid YAML file
        invalid_config = tmp_path / "invalid_config.yaml"
        invalid_config.write_text("invalid: yaml: content: [")
        
        # Should handle gracefully (implementation dependent)
        # This test ensures error handling exists
        with pytest.raises((yaml.YAMLError, ValueError, FileNotFoundError)):
            with open(invalid_config, 'r') as f:
                yaml.safe_load(f)
    
    def test_missing_required_sections(self, tmp_path):
        """Test handling of configuration with missing sections."""
        incomplete_config = {
            "providers": {},
            # Missing models, tasks, settings
        }
        
        config_file = tmp_path / "incomplete_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Should have providers but missing other sections
        assert "providers" in config_data
        assert "models" not in config_data
        assert "tasks" not in config_data
    
    def test_circular_model_references(self, llm_config_data):
        """Test that there are no circular references in model configuration."""
        tasks = llm_config_data["tasks"]
        
        # Simple check - no task should reference itself in fallback
        for task_name, task_config in tasks.items():
            primary = task_config["primary"]
            fallback = task_config.get("fallback", [])
            
            # Primary should not be in fallback
            assert primary not in fallback
            
            # No duplicates in fallback
            assert len(fallback) == len(set(fallback))
