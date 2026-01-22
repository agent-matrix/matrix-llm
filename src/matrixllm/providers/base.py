from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ModelInfo:
    id: str                 # e.g. "openai/gpt-4o-mini"
    object: str = "model"
    owned_by: str | None = None
    meta: dict[str, Any] | None = None


class Provider(Protocol):
    name: str

    async def list_models(self) -> list[ModelInfo]:
        ...

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        ...

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        ...
