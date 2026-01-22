from __future__ import annotations

from typing import Any
import httpx

from matrixllm.providers.base import ModelInfo


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, *, api_key: str) -> None:
        self.api_key = api_key

    async def list_models(self) -> list[ModelInfo]:
        # Anthropic doesn't provide an always-open public models list endpoint in the same way.
        # Provide curated IDs or keep empty and rely on configured allow-list.
        curated = [
            "anthropic/claude-3-5-sonnet-latest",
            "anthropic/claude-3-5-haiku-latest",
        ]
        return [ModelInfo(id=m, meta={"provider": self.name}) for m in curated]

    def _to_anthropic_messages(self, messages: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
        system = ""
        out: list[dict[str, Any]] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system += (content if isinstance(content, str) else str(content)) + "\n"
            elif role in ("user", "assistant"):
                out.append({"role": role, "content": content if isinstance(content, str) else str(content)})
        return system.strip(), out

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("AnthropicProvider not configured")
        raw_model = model.split("/", 1)[1] if "/" in model else model
        system, anth_msgs = self._to_anthropic_messages(messages)
        payload: dict[str, Any] = {
            "model": raw_model,
            "max_tokens": 1024,
            "messages": anth_msgs,
        }
        if system:
            payload["system"] = system
        if temperature is not None:
            payload["temperature"] = temperature

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json() or {}
        # data["content"] is list of blocks; pick text blocks
        blocks = data.get("content") or []
        out = ""
        for b in blocks:
            if (b or {}).get("type") == "text":
                out += (b or {}).get("text") or ""
        return out

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        raise RuntimeError("Anthropic embeddings not implemented in MVP")
