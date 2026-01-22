from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment and optional .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    APP_NAME: str = "MatrixLLM"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 11435
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Auth (comma-separated API keys). Works for Teams agents: Authorization: Bearer OR X-API-Key
    API_KEYS: str = "dev-key-change-me"

    # Rate limiting (slowapi syntax)
    RATE_LIMIT: str = "60/minute"

    # --- Provider: Local Ollama (existing default) ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_PATH: str = "/api/chat"
    OLLAMA_EMBED_PATH: str = "/api/embeddings"

    DEFAULT_MODEL: str = "deepseek-r1"
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

    # ---- Backward compatibility aliases (read old envs if present) ----
    # If user still has OLLABRIDGE_* envs, they can keep working via .env updates manually.
    # (We don't auto-map to keep behavior explicit.)


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
