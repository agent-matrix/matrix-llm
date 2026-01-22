from __future__ import annotations

from typing import Any
import httpx

from matrixllm.providers.base import ModelInfo


class GeminiProvider:
    """
    Minimal Gemini (AI Studio) REST adapter.
    NOTE: Google APIs evolve; this is an MVP adapter. You may want to replace with official SDK later.
    """
    name = "gemini"

    def __init__(self, *, api_key: str) -> None:
        self.api_key = api_key

    async def list_models(self) -> list[ModelInfo]:
        # Curated; keep stable IDs you support
        curated = [
            "google/gemini-1.5-pro",
            "google/gemini-1.5-flash",
        ]
        return [ModelInfo(id=m, meta={"provider": self.name}) for m in curated]

    def _to_prompt(self, messages: list[dict[str, Any]]) -> str:
        sys = ""
        parts: list[str] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                sys += (content if isinstance(content, str) else str(content)) + "\n"
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        return (f"System:\n{sys}\n" if sys.strip() else "") + "\n".join(parts)

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("GeminiProvider not configured")
        raw_model = model.split("/", 1)[1] if "/" in model else model
        prompt = self._to_prompt(messages)

        # Gemini REST endpoint format varies; this uses a common pattern:
        # POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=...
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{raw_model}:generateContent"
        params = {"key": self.api_key}
        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        if temperature is not None:
            payload["generationConfig"] = {"temperature": temperature}

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, params=params, json=payload)
            r.raise_for_status()
            data = r.json() or {}

        # Extract text
        cands = data.get("candidates") or []
        parts = (((cands[0] or {}).get("content") or {}).get("parts") or [])
        txt = ""
        for p in parts:
            if "text" in (p or {}):
                txt += p.get("text") or ""
        return txt

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        raise RuntimeError("Gemini embeddings not implemented in MVP")
