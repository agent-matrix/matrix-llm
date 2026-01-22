from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_with_ollabridge_fallback(primary: str, ollabridge_alias: str, default: str = "") -> str:
    """Get env var with fallback to ollabridge-compatible alias (OLLAS_* prefix)."""
    return os.getenv(primary) or os.getenv(ollabridge_alias) or default


class Settings(BaseSettings):
    """Runtime configuration loaded from environment and optional .env file.

    Supports ollabridge compatibility with OLLAS_* prefixed environment variables:
      - OLLAS_API_KEY -> API_KEYS
      - OLLAS_BASE_URL -> Client base URL (http://localhost:11435/v1)
      - OLLAS_MODEL -> DEFAULT_MODEL
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    APP_NAME: str = "MatrixLLM"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 11435
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Auth (comma-separated API keys). Works for Teams agents: Authorization: Bearer OR X-API-Key
    # Also supports OLLAS_API_KEY for ollabridge compatibility
    API_KEYS: str = _get_env_with_ollabridge_fallback("API_KEYS", "OLLAS_API_KEY", "dev-key-change-me")

    # Auth mode:
    #   - required (default): always require API key (current behavior)
    #   - local-trust: allow requests without key only from loopback (127.0.0.1/::1)
    #   - pairing: require pairing token; expose /pair endpoints for local pairing
    AUTH_MODE: str = os.getenv("AUTH_MODE", "required")

    # Pairing configuration (used when AUTH_MODE=pairing)
    PAIRING_CODE_TTL_SECONDS: int = int(os.getenv("PAIRING_CODE_TTL_SECONDS", "120"))
    PAIRING_LOCAL_ONLY: bool = os.getenv("PAIRING_LOCAL_ONLY", "true").lower() in ("1", "true", "yes", "y")

    @property
    def PAIRING_TOKENS_FILE(self) -> Path:
        return self.DATA_DIR / "pair_tokens.json"

    # Rate limiting (slowapi syntax)
    RATE_LIMIT: str = "60/minute"

    # --- Provider: Local Ollama (existing default) ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_PATH: str = "/api/chat"
    OLLAMA_EMBED_PATH: str = "/api/embeddings"

    # Model defaults (also supports OLLAS_MODEL for ollabridge compatibility)
    DEFAULT_MODEL: str = _get_env_with_ollabridge_fallback("DEFAULT_MODEL", "OLLAS_MODEL", "deepseek-r1")
    DEFAULT_EMBED_MODEL: str = "nomic-embed-text"

    # --- Provider: OpenAI-compatible upstream (OpenAI, Azure OpenAI compat, OpenRouter, vLLM OpenAI server, etc.) ---
    # If set, you can route models like "openai/gpt-4o-mini" or "compat/<model>"
    OPENAI_COMPAT_BASE_URL: str = ""
    OPENAI_COMPAT_API_KEY: str = ""

    # --- Provider: Anthropic (Claude) ---
    ANTHROPIC_API_KEY: str = ""

    # --- Provider: Google Gemini (AI Studio API key; optional) ---
    GEMINI_API_KEY: str = ""

    # --- Provider: IBM watsonx.ai ---
    WATSONX_BASE_URL: str = ""          # e.g. https://us-south.ml.cloud.ibm.com
    WATSONX_API_KEY: str = ""           # IBM Cloud API key (IAM exchange)
    WATSONX_PROJECT_ID: str = ""
    WATSONX_VERSION: str = "2025-02-11" # API version date

    # Routing strategy (simple MVP): prefix|fallback
    ROUTING_MODE: str = "prefix"  # prefix | fallback

    # Control-plane / Node enrollment (relay fabric)
    MODE: str = "gateway"  # gateway | node
    RELAY_ENABLED: bool = True
    ENROLLMENT_SECRET: str = "dev-enroll-change-me"
    ENROLLMENT_TTL_SECONDS: int = 3600

    # When running in gateway mode, register local runtime as a default node
    LOCAL_RUNTIME_ENABLED: bool = True
    LOCAL_NODE_ID: str = "local"
    LOCAL_NODE_TAGS: str = "local"

    # Database
    DATA_DIR: Path = Path.home() / ".matrixllm"
    DATABASE_URL: str | None = None

    @property
    def KEYS_FILE(self) -> Path:
        return self.DATA_DIR / "keys.json"

    # ---- Ollabridge compatibility (client-side aliases) ----
    # These are used by external clients (notebooks, scripts) for ollabridge compatibility
    # OLLAS_BASE_URL is an alias for the client to connect to MatrixLLM
    # OLLAS_API_KEY is handled above via _get_env_with_ollabridge_fallback

    @property
    def OLLAS_BASE_URL(self) -> str:
        """Ollabridge-compatible base URL for clients."""
        return os.getenv("OLLAS_BASE_URL") or f"http://localhost:{self.PORT}/v1"

    @property
    def OLLAS_API_KEY(self) -> str:
        """Ollabridge-compatible API key (returns the first configured key)."""
        keys = self.API_KEYS.split(",")
        return keys[0].strip() if keys else ""

    @property
    def OLLAS_MODEL(self) -> str:
        """Ollabridge-compatible default model."""
        return os.getenv("OLLAS_MODEL") or self.DEFAULT_MODEL


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
