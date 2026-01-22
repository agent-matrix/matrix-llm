from __future__ import annotations

from typing import Any
import httpx

from matrixllm.providers.base import ModelInfo


class OpenAICompatProvider:
    """
    Calls any OpenAI-compatible endpoint:
      - OpenAI
      - Azure OpenAI (compat endpoints)
      - OpenRouter-like gateways
      - vLLM OpenAI server
      - Ollama OpenAI compatibility layers (if any)
    """

    def __init__(self, *, base_url: str, api_key: str, name: str = "openai_compat") -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def list_models(self) -> list[ModelInfo]:
        if not self.base_url or not self.api_key:
            return []
        url = f"{self.base_url}/models"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
            r.raise_for_status()
            data = r.json() or {}
        items = data.get("data") or []
        out: list[ModelInfo] = []
        for it in items:
            mid = it.get("id")
            if mid:
                out.append(ModelInfo(id=f"openai/{mid}", owned_by=it.get("owned_by"), meta={"provider": self.name}))
        return out

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        if not self.base_url or not self.api_key:
            raise RuntimeError("OpenAICompatProvider not configured")
        # model is expected namespaced: "openai/<id>" OR "compat/<id>"
        raw_model = model.split("/", 1)[1] if "/" in model else model
        payload: dict[str, Any] = {"model": raw_model, "messages": messages}
        if temperature is not None:
            payload["temperature"] = temperature
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json() or {}
        # OpenAI-compatible response
        choices = data.get("choices") or []
        msg = (choices[0] or {}).get("message") or {}
        return msg.get("content") or ""

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        if not self.base_url or not self.api_key:
            raise RuntimeError("OpenAICompatProvider not configured")
        raw_model = model.split("/", 1)[1] if "/" in model else model
        payload = {"model": raw_model, "input": text}
        url = f"{self.base_url}/embeddings"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json() or {}
        arr = (data.get("data") or [])
        emb = (arr[0] or {}).get("embedding") or []
        return emb
