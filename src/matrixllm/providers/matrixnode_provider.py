from __future__ import annotations

from typing import Any

from matrixllm.core.registry import RuntimeRegistry
from matrixllm.core.router import Router
from matrixllm.api.relay import RelayHub
from matrixllm.providers.base import ModelInfo


class MatrixNodeProvider:
    """
    Wraps the existing matrixllm relay/direct/local node fabric as a MatrixLLM provider.
    - Uses RuntimeRegistry + Router to pick a node.
    - Uses RelayHub for relay_link nodes.
    - Uses direct endpoint connector for direct_endpoint nodes.
    - Uses local ollama provider for local_ollama nodes.
    """
    name = "matrixnode"

    def __init__(self, *, registry: RuntimeRegistry, router: Router, relay_hub: RelayHub, direct: Any) -> None:
        self.registry = registry
        self.router = router
        self.relay_hub = relay_hub
        self.direct = direct

    async def list_models(self) -> list[ModelInfo]:
        # Best-effort union:
        # - Ask one healthy node for its models, plus local ollama if available
        out: list[ModelInfo] = []
        try:
            decision = await self.router.choose_node()
            node = decision.node
            if node.connector == "relay_link":
                frame = await self.relay_hub.request(node.node_id, "models", {})
                data = frame.get("data") or {}
                items = data.get("data") or []
                for it in items:
                    mid = it.get("id")
                    if mid:
                        out.append(ModelInfo(id=f"matrixnode/{mid}", meta={"via": "relay"}))
            elif node.connector == "direct_endpoint":
                data = await self.direct.models(base=node.endpoint or "")
                for it in (data.get("data") or []):
                    mid = it.get("id")
                    if mid:
                        out.append(ModelInfo(id=f"matrixnode/{mid}", meta={"via": "direct"}))
            else:
                from matrixllm.providers.ollama_client import list_models as ollama_list
                models = await ollama_list()
                for m in models:
                    out.append(ModelInfo(id=f"matrixnode/{m}", meta={"via": "local_ollama"}))
        except Exception:
            pass
        return out

    async def chat(self, *, model: str, messages: list[dict[str, Any]], temperature: float | None = None) -> str:
        # model expected: matrixnode/<model>
        raw_model = model.split("/", 1)[1] if "/" in model else model
        decision = await self.router.choose_node(model=raw_model)
        node = decision.node
        if node.connector == "relay_link":
            frame = await self.relay_hub.request(node.node_id, "chat", {"model": raw_model, "messages": messages})
            if not frame.get("ok", True):
                raise RuntimeError(frame.get("error") or "upstream error")
            return ((frame.get("data") or {}).get("content")) or ""
        if node.connector == "direct_endpoint":
            data = await self.direct.chat(base=node.endpoint or "", payload={"model": raw_model, "messages": messages})
            return data.get("content") or ""
        # local_ollama fallback
        from matrixllm.providers.ollama_client import chat as ollama_chat
        return await ollama_chat(model=raw_model, messages=messages)

    async def embeddings(self, *, model: str, text: str) -> list[float]:
        raw_model = model.split("/", 1)[1] if "/" in model else model
        decision = await self.router.choose_node(model=raw_model)
        node = decision.node
        if node.connector == "relay_link":
            frame = await self.relay_hub.request(node.node_id, "embeddings", {"model": raw_model, "input": text})
            if not frame.get("ok", True):
                raise RuntimeError(frame.get("error") or "upstream error")
            return ((frame.get("data") or {}).get("embedding")) or []
        if node.connector == "direct_endpoint":
            data = await self.direct.embeddings(base=node.endpoint or "", payload={"model": raw_model, "input": text})
            return data.get("embedding") or []
        from matrixllm.providers.ollama_client import embeddings as ollama_embed
        return await ollama_embed(model=raw_model, text=text)
