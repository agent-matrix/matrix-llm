"""Provider configuration and preferences management.

Handles storing and loading user preferences for LLM provider selection.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from matrixllm.core.settings import settings


# Provider metadata
PROVIDER_INFO = {
    "ollama": {
        "name": "Ollama (Local)",
        "description": "Local Ollama instance for running open-source models",
        "env_vars": ["OLLAMA_BASE_URL"],
        "required_vars": [],  # Ollama is auto-installed
        "model_prefix": None,  # No prefix needed
        "example_models": ["deepseek-r1", "llama3.1:8b", "qwen2.5:7b"],
    },
    "openai": {
        "name": "OpenAI",
        "description": "OpenAI API (GPT-4, GPT-3.5, etc.)",
        "env_vars": ["OPENAI_COMPAT_BASE_URL", "OPENAI_COMPAT_API_KEY"],
        "required_vars": ["OPENAI_COMPAT_BASE_URL", "OPENAI_COMPAT_API_KEY"],
        "model_prefix": "openai/",
        "example_models": ["openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-3.5-turbo"],
    },
    "anthropic": {
        "name": "Anthropic",
        "description": "Anthropic Claude models",
        "env_vars": ["ANTHROPIC_API_KEY"],
        "required_vars": ["ANTHROPIC_API_KEY"],
        "model_prefix": "anthropic/",
        "example_models": ["anthropic/claude-3-5-sonnet-latest", "anthropic/claude-3-opus-latest"],
    },
    "google": {
        "name": "Google Gemini",
        "description": "Google AI Studio / Gemini models",
        "env_vars": ["GEMINI_API_KEY"],
        "required_vars": ["GEMINI_API_KEY"],
        "model_prefix": "google/",
        "example_models": ["google/gemini-1.5-pro", "google/gemini-1.5-flash"],
    },
    "watsonx": {
        "name": "IBM watsonx.ai",
        "description": "IBM watsonx.ai with Granite models",
        "env_vars": ["WATSONX_BASE_URL", "WATSONX_API_KEY", "WATSONX_PROJECT_ID"],
        "required_vars": ["WATSONX_BASE_URL", "WATSONX_API_KEY", "WATSONX_PROJECT_ID"],
        "model_prefix": "ibm/",
        "example_models": ["ibm/granite-3-8b-instruct", "ibm/granite-3-2b-instruct"],
    },
}


@dataclass
class ProviderPreferences:
    """User preferences for provider selection."""
    default_provider: str = "ollama"
    default_models: dict = field(default_factory=dict)  # provider -> model mapping

    def to_dict(self) -> dict:
        return {
            "default_provider": self.default_provider,
            "default_models": self.default_models,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProviderPreferences":
        return cls(
            default_provider=data.get("default_provider", "ollama"),
            default_models=data.get("default_models", {}),
        )


def get_config_path() -> Path:
    """Get the path to the provider config file."""
    return settings.DATA_DIR / "provider_config.json"


def load_preferences() -> ProviderPreferences:
    """Load provider preferences from config file."""
    config_path = get_config_path()
    if not config_path.exists():
        return ProviderPreferences()
    try:
        data = json.loads(config_path.read_text())
        return ProviderPreferences.from_dict(data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return ProviderPreferences()


def save_preferences(prefs: ProviderPreferences) -> None:
    """Save provider preferences to config file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(prefs.to_dict(), indent=2))


def is_provider_configured(provider: str) -> bool:
    """Check if a provider has all required environment variables set."""
    info = PROVIDER_INFO.get(provider)
    if not info:
        return False

    # Ollama is always "configured" (self-healing install)
    if provider == "ollama":
        return True

    # Check required environment variables
    for var in info["required_vars"]:
        if not os.getenv(var) and not getattr(settings, var, None):
            return False
    return True


def get_configured_providers() -> list[str]:
    """Get list of all configured providers."""
    return [p for p in PROVIDER_INFO.keys() if is_provider_configured(p)]


def get_provider_status() -> dict[str, dict]:
    """Get status of all providers with configuration details."""
    result = {}
    for provider, info in PROVIDER_INFO.items():
        configured = is_provider_configured(provider)
        missing_vars = []

        if not configured:
            for var in info["required_vars"]:
                if not os.getenv(var) and not getattr(settings, var, None):
                    missing_vars.append(var)

        result[provider] = {
            **info,
            "configured": configured,
            "missing_vars": missing_vars,
        }

    return result


def get_default_provider() -> str:
    """Get the current default provider."""
    prefs = load_preferences()
    # Validate that the default provider is still configured
    if is_provider_configured(prefs.default_provider):
        return prefs.default_provider
    # Fall back to first configured provider
    configured = get_configured_providers()
    return configured[0] if configured else "ollama"


def set_default_provider(provider: str) -> tuple[bool, str]:
    """Set the default provider.

    Returns (success, message) tuple.
    """
    if provider not in PROVIDER_INFO:
        available = ", ".join(PROVIDER_INFO.keys())
        return False, f"Unknown provider '{provider}'. Available: {available}"

    if not is_provider_configured(provider):
        info = PROVIDER_INFO[provider]
        missing = info["required_vars"]
        return False, f"Provider '{provider}' is not configured. Set: {', '.join(missing)}"

    prefs = load_preferences()
    prefs.default_provider = provider
    save_preferences(prefs)
    return True, f"Default provider set to '{provider}'"


def get_default_model_for_provider(provider: str) -> Optional[str]:
    """Get the default model for a specific provider."""
    prefs = load_preferences()
    if provider in prefs.default_models:
        return prefs.default_models[provider]

    # Return first example model as default
    info = PROVIDER_INFO.get(provider)
    if info and info["example_models"]:
        return info["example_models"][0]
    return None


def set_default_model_for_provider(provider: str, model: str) -> tuple[bool, str]:
    """Set the default model for a specific provider."""
    if provider not in PROVIDER_INFO:
        return False, f"Unknown provider '{provider}'"

    prefs = load_preferences()
    prefs.default_models[provider] = model
    save_preferences(prefs)
    return True, f"Default model for '{provider}' set to '{model}'"
