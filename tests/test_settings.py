"""Tests for the settings module."""

import os
from pathlib import Path
from unittest.mock import patch

from matrixllm.core.settings import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = Settings()
        assert settings.APP_NAME == "MatrixLLM"
        assert settings.ENV == "dev"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 11435

    def test_default_ollama_config(self):
        """Test default Ollama configuration."""
        settings = Settings()
        assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
        assert settings.OLLAMA_CHAT_PATH == "/api/chat"
        assert settings.OLLAMA_EMBED_PATH == "/api/embeddings"

    def test_default_model(self):
        """Test default model settings."""
        settings = Settings()
        assert settings.DEFAULT_MODEL == "deepseek-r1"
        assert settings.DEFAULT_EMBED_MODEL == "nomic-embed-text"

    def test_default_api_keys(self):
        """Test default API keys."""
        settings = Settings()
        assert settings.API_KEYS == "dev-key-change-me"

    def test_default_rate_limit(self):
        """Test default rate limit."""
        settings = Settings()
        assert settings.RATE_LIMIT == "60/minute"

    def test_default_routing_mode(self):
        """Test default routing mode."""
        settings = Settings()
        assert settings.ROUTING_MODE == "prefix"

    def test_default_mode(self):
        """Test default mode."""
        settings = Settings()
        assert settings.MODE == "gateway"

    def test_relay_enabled_default(self):
        """Test relay enabled by default."""
        settings = Settings()
        assert settings.RELAY_ENABLED is True

    def test_local_runtime_enabled_default(self):
        """Test local runtime enabled by default."""
        settings = Settings()
        assert settings.LOCAL_RUNTIME_ENABLED is True
        assert settings.LOCAL_NODE_ID == "local"

    def test_data_dir_is_path(self):
        """Test DATA_DIR is a Path object."""
        settings = Settings()
        assert isinstance(settings.DATA_DIR, Path)

    def test_keys_file_property(self):
        """Test KEYS_FILE property returns correct path."""
        settings = Settings()
        expected = settings.DATA_DIR / "keys.json"
        assert settings.KEYS_FILE == expected

    def test_cors_origins_default(self):
        """Test default CORS origins."""
        settings = Settings()
        assert "localhost:5173" in settings.CORS_ORIGINS
        assert "localhost:3000" in settings.CORS_ORIGINS

    def test_enrollment_settings(self):
        """Test enrollment settings defaults."""
        settings = Settings()
        assert settings.ENROLLMENT_SECRET == "dev-enroll-change-me"
        assert settings.ENROLLMENT_TTL_SECONDS == 3600

    @patch.dict(os.environ, {"APP_NAME": "TestApp"})
    def test_env_override(self):
        """Test that environment variables override defaults."""
        settings = Settings()
        assert settings.APP_NAME == "TestApp"

    @patch.dict(os.environ, {"PORT": "8080"})
    def test_env_override_port(self):
        """Test that PORT environment variable is parsed correctly."""
        settings = Settings()
        assert settings.PORT == 8080

    def test_provider_api_keys_empty_default(self):
        """Test that provider API keys are empty by default."""
        settings = Settings()
        assert settings.OPENAI_COMPAT_API_KEY == ""
        assert settings.ANTHROPIC_API_KEY == ""
        assert settings.GEMINI_API_KEY == ""
        assert settings.WATSONX_API_KEY == ""


class TestOllabridgeCompatibility:
    """Tests for ollabridge compatibility (OLLAS_* environment variables)."""

    def test_ollas_base_url_property(self):
        """Test OLLAS_BASE_URL property returns correct URL."""
        settings = Settings()
        expected = f"http://localhost:{settings.PORT}/v1"
        assert settings.OLLAS_BASE_URL == expected

    def test_ollas_api_key_property(self):
        """Test OLLAS_API_KEY property returns first API key."""
        settings = Settings()
        # Default is "dev-key-change-me"
        assert settings.OLLAS_API_KEY == "dev-key-change-me"

    def test_ollas_model_property(self):
        """Test OLLAS_MODEL property returns default model."""
        settings = Settings()
        assert settings.OLLAS_MODEL == "deepseek-r1"

    @patch.dict(os.environ, {"OLLAS_API_KEY": "sk-ollabridge-test-key"}, clear=False)
    def test_ollas_api_key_fallback(self):
        """Test that OLLAS_API_KEY env var is used as fallback for API_KEYS."""
        # Clear API_KEYS so OLLAS_API_KEY is used
        with patch.dict(os.environ, {"API_KEYS": ""}, clear=False):
            from matrixllm.core.settings import _get_env_with_ollabridge_fallback
            result = _get_env_with_ollabridge_fallback("API_KEYS", "OLLAS_API_KEY", "default")
            assert result == "sk-ollabridge-test-key"

    @patch.dict(os.environ, {"OLLAS_BASE_URL": "http://custom:8080/v1"}, clear=False)
    def test_ollas_base_url_override(self):
        """Test that OLLAS_BASE_URL env var overrides default."""
        settings = Settings()
        assert settings.OLLAS_BASE_URL == "http://custom:8080/v1"

    @patch.dict(os.environ, {"OLLAS_MODEL": "llama3"}, clear=False)
    def test_ollas_model_override(self):
        """Test that OLLAS_MODEL env var overrides default."""
        settings = Settings()
        assert settings.OLLAS_MODEL == "llama3"

    @patch.dict(os.environ, {"API_KEYS": "primary-key,secondary-key"}, clear=False)
    def test_ollas_api_key_returns_first_key(self):
        """Test that OLLAS_API_KEY returns only the first key from comma-separated list."""
        settings = Settings()
        assert settings.OLLAS_API_KEY == "primary-key"

    def test_api_keys_prefers_primary_over_ollas(self):
        """Test that API_KEYS takes priority over OLLAS_API_KEY."""
        from matrixllm.core.settings import _get_env_with_ollabridge_fallback
        with patch.dict(os.environ, {"API_KEYS": "primary", "OLLAS_API_KEY": "ollas"}, clear=False):
            result = _get_env_with_ollabridge_fallback("API_KEYS", "OLLAS_API_KEY", "default")
            assert result == "primary"
