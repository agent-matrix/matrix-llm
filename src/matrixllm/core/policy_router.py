from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrixllm.core.settings import settings
from matrixllm.core.provider_config import get_default_provider, PROVIDER_INFO
from matrixllm.providers.base import Provider


@dataclass(frozen=True)
class ProviderDecision:
    provider: Provider
    model: str


# Map provider config names to internal provider keys
PROVIDER_KEY_MAP = {
    "ollama": "matrixnode",  # ollama uses matrixnode provider
    "openai": "openai",
    "anthropic": "anthropic",
    "google": "google",
    "watsonx": "ibm",
}


class PolicyRouter:
    """
    MVP policy router:
      - ROUTING_MODE=prefix: choose provider by model namespace prefix
      - ROUTING_MODE=fallback: try a chain (matrixnode -> openai -> anthropic -> gemini -> watsonx) based on config
      - Respects user's default provider preference for models without a prefix
    """

    def __init__(self, providers: dict[str, Provider]) -> None:
        self.providers = providers

    def _provider_from_model(self, model: str) -> str:
        if "/" in model:
            prefix = model.split("/", 1)[0].strip().lower()
            return prefix
        # No prefix - use user's default provider preference
        default_provider = get_default_provider()
        return PROVIDER_KEY_MAP.get(default_provider, "matrixnode")

    async def list_models(self) -> list[dict[str, Any]]:
        # Aggregate models from all configured providers
        data: list[dict[str, Any]] = []
        for _, p in self.providers.items():
            try:
                models = await p.list_models()
                for m in models:
                    data.append({"id": m.id, "object": "model"})
            except Exception:
                continue
        # de-dupe by id
        seen = set()
        uniq = []
        for it in data:
            mid = it.get("id")
            if mid and mid not in seen:
                seen.add(mid)
                uniq.append(it)
        return uniq

    async def decide(self, model: str) -> ProviderDecision:
        mode = (settings.ROUTING_MODE or "prefix").lower()

        if mode == "prefix":
            key = self._provider_from_model(model)
            has_prefix = "/" in model

            # allow aliases
            if key in ("compat", "openai"):
                key = "openai"
            if key in ("anthropic",):
                key = "anthropic"
            if key in ("google", "gemini"):
                key = "google"
            if key in ("ibm", "watsonx"):
                key = "ibm"
            if key in ("matrixnode", "node", "ollama"):
                key = "matrixnode"

            if key == "openai" and "openai" in self.providers:
                # For non-prefixed models routed to openai, add prefix
                if not has_prefix:
                    model = f"openai/{model}"
                return ProviderDecision(provider=self.providers["openai"], model=model)
            if key == "anthropic" and "anthropic" in self.providers:
                if not has_prefix:
                    model = f"anthropic/{model}"
                return ProviderDecision(provider=self.providers["anthropic"], model=model)
            if key == "google" and "google" in self.providers:
                if not has_prefix:
                    model = f"google/{model}"
                return ProviderDecision(provider=self.providers["google"], model=model)
            if key == "ibm" and "ibm" in self.providers:
                if not has_prefix:
                    model = f"ibm/{model}"
                return ProviderDecision(provider=self.providers["ibm"], model=model)
            # default to matrixnode if present
            if "matrixnode" in self.providers:
                # if model wasn't namespaced, treat it as matrixnode/<model>
                if "/" not in model:
                    model = f"matrixnode/{model}"
                return ProviderDecision(provider=self.providers["matrixnode"], model=model)
            raise RuntimeError(f"No provider available for model: {model}")

        # fallback mode - respect default provider order
        default_provider = get_default_provider()
        default_key = PROVIDER_KEY_MAP.get(default_provider, "matrixnode")

        # Put default provider first in chain
        chain = ["matrixnode", "openai", "anthropic", "google", "ibm"]
        if default_key in chain:
            chain.remove(default_key)
            chain.insert(0, default_key)

        for k in chain:
            if k in self.providers:
                # normalize model for some providers
                if k == "matrixnode" and not model.startswith("matrixnode/") and "/" not in model:
                    mm = f"matrixnode/{model}"
                else:
                    mm = model
                return ProviderDecision(provider=self.providers[k], model=mm)
        raise RuntimeError("No providers configured")
