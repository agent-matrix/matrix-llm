from __future__ import annotations

from typing import Any
import httpx

from matrixllm.providers.base import ModelInfo


class WatsonxProvider:
    """
    IBM watsonx.ai (native REST) MVP:
      - IAM token exchange: POST https://iam.cloud.ibm.com/identity/token
      - Text generation: POST {base}/ml/v1/text/generation?version=YYYY-MM-DD
    """
    name = "watsonx"

    def __init__(self, *, base_url: str, api_key: str, project_id: str, version: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.project_id = project_id
        self.version = version

    async def list_models(self) -> list[ModelInfo]:
        # Curated list. You can extend to dynamic catalog later.
        curated = [
            "ibm/granite-3-8b-instruct",
            "ibm/granite-3-2b-instruct",
        ]
        return [ModelInfo(id=m, meta={"provider": self.name}) for m in curated]

    async def _iam_token(self) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data="grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=" + self.api_key,
            )
            r.raise_for_status()
            data = r.json() or {}
        tok = data.get("access_token")
        if not tok:
            raise RuntimeError("watsonx IAM token missing")
        return tok

    def _to_prompt(self, messages: list[dict[str, Any]]) -> str:
        sys = ""
        parts: list[str] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                sys += (content if isinstance(content, str) else str(content)) + "\n"
            elif role == "user":
                parts.append(content if isinstance(content, str) else str(content))
            elif role == "assistant":
                parts.append(f"(assistant said: {content if isinstance(content, str) else str(content)})")
        return (f"System:\n{sys}\n" if sys.strip() else "") + "\n".join(parts)

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        if not (self.base_url and self.api_key and self.project_id and self.version):
            raise RuntimeError("WatsonxProvider not configured")
        tok = await self._iam_token()
        prompt = self._to_prompt(messages)

        # model expected: ibm/<model_id> or watsonx/<model_id>
        raw_model = model.split("/", 1)[1] if "/" in model else model

        payload: dict[str, Any] = {
            "input": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": temperature if temperature is not None else 0.2,
            },
            "model_id": raw_model,
            "project_id": self.project_id,
        }
        url = f"{self.base_url}/ml/v1/text/generation"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                url,
                params={"version": self.version},
                headers={"Authorization": f"Bearer {tok}", "Accept": "application/json", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json() or {}

        results = data.get("results") or []
        if results:
            return (results[0] or {}).get("generated_text") or ""
        return data.get("generated_text") or ""

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        raise RuntimeError("watsonx embeddings not implemented in MVP")
