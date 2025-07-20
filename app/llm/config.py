"""
LLM Configuration module

Handles configuration for different LLM models and providers.
Supports OpenAI-compatible endpoints including open source models.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    DEEPINFRA = "deepinfra"
    CUSTOM_OPENAI_COMPATIBLE = "custom_openai_compatible"


class ModelConfig(BaseModel):
    """Configuration for a specific model"""

    name: str
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = Field(default=2048, ge=1, le=1047576)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    timeout: int = Field(default=60, ge=1)

    class Config:
        use_enum_values = True


class LLMConfig:
    """Main LLM configuration class"""

    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.models: Dict[str, ModelConfig] = {}
        self.task_models: Dict[str, str] = {}
        self.enable_caching: bool = True
        self.cache_ttl: int = 3600
        self.max_concurrent_requests: int = 5
        self.enable_monitoring: bool = True
        self.default_timeout: int = 60
        self.retry_attempts: int = 3
        self.retry_delay: float = 1.0
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent.parent / "llm_config.yaml"

        # Load YAML configuration
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)
            self._yaml_config = yaml_config  # Store for fallback method usage
        except FileNotFoundError:
            print(
                f"Warning: LLM config file not found at {config_path}. Using fallback configuration."
            )
            self._load_fallback_config()
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config: {e}. Using fallback configuration.")
            self._load_fallback_config()
            return

        # Parse providers configuration
        self.providers = yaml_config.get("providers", {})

        # Parse models configuration
        models_config = yaml_config.get("models", {})
        self.models = {}

        for model_name, model_data in models_config.items():
            provider_name = model_data.get("provider")
            provider_config = self.providers.get(provider_name, {})

            # Get API key from environment if required
            api_key = None
            if provider_config.get("requires_api_key", False):
                api_key_env = provider_config.get("api_key_env")
                if api_key_env:
                    api_key = os.getenv(api_key_env)

            # Get base URL
            base_url = provider_config.get("base_url")
            if not base_url:
                base_url_env = provider_config.get("base_url_env")
                if base_url_env:
                    base_url = os.getenv(
                        base_url_env, provider_config.get("default_base_url")
                    )
                else:
                    base_url = provider_config.get("default_base_url")

            self.models[model_name] = ModelConfig(
                name=model_name,
                provider=ModelProvider(provider_name),
                api_key=api_key,
                base_url=base_url,
                max_tokens=model_data.get("max_tokens", 2048),
                temperature=model_data.get("temperature", 0.7),
            )

        # Parse task model assignments
        tasks_config = yaml_config.get("tasks", {})
        self.task_models = {}

        for task_name, task_data in tasks_config.items():
            # Check for environment variable override
            env_var = (
                yaml_config.get("settings", {}).get("env_overrides", {}).get(task_name)
            )
            if env_var:
                override_model = os.getenv(env_var)
                if override_model:
                    self.task_models[task_name] = override_model
                    continue

            # Use primary model from config
            primary_model = task_data.get("primary")
            if primary_model:
                self.task_models[task_name] = primary_model

        # Parse general settings
        settings = yaml_config.get("settings", {})
        self.enable_caching = settings.get("enable_caching", True)
        self.cache_ttl = settings.get("cache_ttl_seconds", 3600)
        self.max_concurrent_requests = settings.get("max_concurrent_requests", 5)
        self.enable_monitoring = settings.get("enable_monitoring", True)
        self.default_timeout = settings.get("default_timeout", 60)
        self.retry_attempts = settings.get("retry_attempts", 3)
        self.retry_delay = settings.get("retry_delay", 1.0)

    def _load_fallback_config(self):
        """Load fallback configuration when YAML file is not available"""

        # Default model configurations
        self.models = {
            "gpt-4.1": ModelConfig(
                name="gpt-4.1",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=8192,
                temperature=0.7,
            ),
            "gpt-4.1-mini": ModelConfig(
                name="gpt-4.1-mini",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=8192,
                temperature=0.7,
            ),
            " gpt-4.1-nano": ModelConfig(
                name="gpt-4.1-nano",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=8192,
                temperature=0.7,
            ),
        }

        # Default model preferences for different tasks
        self.task_models = {
            "story_generation": os.getenv("LLM_STORY_MODEL", "gpt-4.1-mini"),
            "analysis": os.getenv("LLM_ANALYSIS_MODEL", "gpt-4.1-mini"),
            "summarization": os.getenv("LLM_SUMMARY_MODEL", "gpt-4.1-nano"),
            "translation": os.getenv("LLM_TRANSLATION_MODEL", "gpt-4.1-nano"),
            "improvement": os.getenv("LLM_IMPROVEMENT_MODEL", "gpt-4.1"),
        }

        # General settings
        self.enable_caching = os.getenv("LLM_ENABLE_CACHING", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hour
        self.max_concurrent_requests = int(os.getenv("LLM_MAX_CONCURRENT", "5"))
        self.enable_monitoring = (
            os.getenv("LLM_ENABLE_MONITORING", "true").lower() == "true"
        )

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_name)

    def get_task_model(self, task: str) -> str:
        """Get preferred model for a specific task"""
        return self.task_models.get(task, "gpt-4.1-mini")

    def add_custom_model(self, model_config: ModelConfig):
        """Add a custom model configuration"""
        self.models[model_config.name] = model_config

    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available"""
        config = self.get_model_config(model_name)
        if not config:
            return False

        # For OpenAI and DeepInfra models, check if API key is available
        if config.provider in [ModelProvider.OPENAI, ModelProvider.DEEPINFRA]:
            return (
                config.api_key is not None
                and config.api_key.strip() != ""
                and config.api_key != "your-openai-api-key-here"
                and not config.api_key.startswith("your-")
            )

        # For CUSTOM_OPENAI_COMPATIBLE, assume available if base_url is set
        # In production, you might want to add actual connectivity checks
        if config.provider in [ModelProvider.CUSTOM_OPENAI_COMPATIBLE]:
            return config.base_url is not None and config.base_url.strip() != ""

        return False

    def get_task_model_with_fallback(self, task: str) -> str:
        """Get preferred model for a task, with fallback to available models"""
        primary_model = self.get_task_model(task)

        # Check if primary model is available
        if self.is_model_available(primary_model):
            return primary_model

        # Try fallback models from YAML config
        if hasattr(self, "_yaml_config"):
            task_config = self._yaml_config.get("tasks", {}).get(task, {})
            fallback_models = task_config.get("fallback", [])

            for fallback_model in fallback_models:
                if self.is_model_available(fallback_model):
                    return fallback_model

        # Last resort: find any available model
        for model_name in self.models.keys():
            if self.is_model_available(model_name):
                return model_name

        # If nothing is available, return the primary model anyway
        return primary_model

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get provider configuration"""
        return self.providers.get(provider_name, {})

    def list_available_models(self) -> List[str]:
        """List all available models"""
        return [name for name in self.models.keys() if self.is_model_available(name)]

    def list_models_by_task(self, task: str) -> List[str]:
        """List models suitable for a specific task"""
        # Get primary and fallback models for the task
        models = []

        primary = self.get_task_model(task)
        if primary:
            models.append(primary)

        if hasattr(self, "_yaml_config"):
            task_config = self._yaml_config.get("tasks", {}).get(task, {})
            fallback_models = task_config.get("fallback", [])
            models.extend(fallback_models)

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for model in models:
            if model not in seen and model in self.models:
                seen.add(model)
                result.append(model)

        return result

    def is_development_mode(self) -> bool:
        """Check if we're running in development mode (no real API keys)"""
        return not any(self.is_model_available(model) for model in self.models.keys())

    def get_model_debug_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed debug information about a model's availability"""
        config = self.get_model_config(model_name)
        if not config:
            return {"error": "Model not found"}

        provider_config = self.get_provider_config(config.provider.value)

        debug_info = {
            "name": model_name,
            "provider": config.provider.value,
            "requires_api_key": provider_config.get("requires_api_key", False),
            "api_key_present": config.api_key is not None,
            "api_key_is_placeholder": False,
            "base_url": config.base_url,
            "available": self.is_model_available(model_name),
        }

        if config.api_key:
            debug_info["api_key_is_placeholder"] = (
                config.api_key.startswith("your-")
                or config.api_key == "your-openai-api-key-here"
            )
            debug_info["api_key_preview"] = (
                config.api_key[:10] + "..."
                if len(config.api_key) > 10
                else config.api_key
            )

        return debug_info


# Global configuration instance
llm_config = LLMConfig()
