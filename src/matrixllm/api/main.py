from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from matrixllm.core.settings import settings
from matrixllm.core.security import require_auth
from matrixllm.core.enrollment import create_join_token
from matrixllm.db.database import init_db, session
from matrixllm.db.models import RequestLog
from matrixllm.api.state import build_state
from matrixllm.api.relay import RelayHub, build_relay_router
from matrixllm.api.pair import router as pair_router
from matrixllm.core.registry import RuntimeNodeState

from matrixllm.providers.openai_compat import OpenAICompatProvider
from matrixllm.providers.anthropic_provider import AnthropicProvider
from matrixllm.providers.gemini_provider import GeminiProvider
from matrixllm.providers.watsonx_provider import WatsonxProvider
from matrixllm.providers.matrixnode_provider import MatrixNodeProvider
from matrixllm.core.policy_router import PolicyRouter


log = logging.getLogger("matrixllm")
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatReq(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    temperature: float | None = None


class EmbeddingsReq(BaseModel):
    model: str | None = None
    input: str


def _parse_origins(raw: str) -> list[str]:
    if not raw:
        return []
    return [o.strip() for o in raw.split(",") if o.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)
    app.state.limiter = limiter

    # Build existing state (registry/router/direct connector)
    app.state.matrix = build_state()
    app.state.relay_hub = RelayHub(app.state.matrix.registry)

    # CORS
    origins = _parse_origins(settings.CORS_ORIGINS)
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.on_event("startup")
    def _startup():
        init_db()
        # Register local runtime as a default node
        if settings.LOCAL_RUNTIME_ENABLED:
            import asyncio
            async def _reg():
                await app.state.matrix.registry.upsert(
                    RuntimeNodeState(
                        node_id=settings.LOCAL_NODE_ID,
                        connector="local_ollama",
                        endpoint=settings.OLLAMA_BASE_URL,
                        tags=[t.strip() for t in settings.LOCAL_NODE_TAGS.split(",") if t.strip()],
                        models=[],
                        capacity=1,
                        meta={"via": "local"},
                    )
                )
            asyncio.get_event_loop().create_task(_reg())

        # Build providers map for PolicyRouter (configured providers only)
        providers: dict[str, Any] = {}

        # Provider: matrixnode (relay/direct/local fabric)
        providers["matrixnode"] = MatrixNodeProvider(
            registry=app.state.matrix.registry,
            router=app.state.matrix.router,
            relay_hub=app.state.relay_hub,
            direct=app.state.matrix.direct,
        )

        # Provider: OpenAI-compatible
        if settings.OPENAI_COMPAT_BASE_URL and settings.OPENAI_COMPAT_API_KEY:
            providers["openai"] = OpenAICompatProvider(
                base_url=settings.OPENAI_COMPAT_BASE_URL,
                api_key=settings.OPENAI_COMPAT_API_KEY,
                name="openai_compat",
            )

        # Provider: Anthropic
        if settings.ANTHROPIC_API_KEY:
            providers["anthropic"] = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)

        # Provider: Gemini
        if settings.GEMINI_API_KEY:
            providers["google"] = GeminiProvider(api_key=settings.GEMINI_API_KEY)

        # Provider: watsonx
        if settings.WATSONX_BASE_URL and settings.WATSONX_API_KEY and settings.WATSONX_PROJECT_ID:
            providers["ibm"] = WatsonxProvider(
                base_url=settings.WATSONX_BASE_URL,
                api_key=settings.WATSONX_API_KEY,
                project_id=settings.WATSONX_PROJECT_ID,
                version=settings.WATSONX_VERSION,
            )

        app.state.providers = providers
        app.state.policy_router = PolicyRouter(providers=providers)

    # Relay enrollment / connect (optional)
    if settings.RELAY_ENABLED:
        app.include_router(build_relay_router(registry=app.state.matrix.registry, hub=app.state.relay_hub))

    # Pairing endpoints (for matrixshell local pairing)
    app.include_router(pair_router)

    @app.get("/health")
    async def health():
        try:
            nodes = await app.state.matrix.registry.list()
            pcount = len(getattr(app.state, "providers", {}) or {})
            return {
                "status": "ok",
                "mode": settings.MODE,
                "routing_mode": settings.ROUTING_MODE,
                "providers": pcount,
                "runtimes": len(nodes),
                "default_model": settings.DEFAULT_MODEL,
            }
        except Exception as e:
            return {"status": "degraded", "detail": str(e)}

    # ----------------------------
    # OpenAI-compatible endpoints
    # ----------------------------
    @app.post("/v1/chat/completions")
    async def chat_completions(req: ChatReq, request: Request, _auth: str = Depends(require_auth)) -> dict[str, Any]:
        model = (req.model or settings.DEFAULT_MODEL)
        t0 = time.time()
        try:
            payload_messages = [{"role": m.role, "content": m.content} for m in req.messages]

            decision = await app.state.policy_router.decide(model)
            content = await decision.provider.chat(model=decision.model, messages=payload_messages, temperature=req.temperature)

            latency = int((time.time() - t0) * 1000)
            with session() as s:
                s.add(
                    RequestLog(
                        path=str(request.url.path),
                        model=model,
                        latency_ms=latency,
                        ok=True,
                        client=request.client.host if request.client else None,
                    )
                )
                s.commit()

            return {
                "id": "matrixllm-chat",
                "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}}],
            }
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            with session() as s:
                s.add(
                    RequestLog(
                        path=str(request.url.path),
                        model=model,
                        latency_ms=latency,
                        ok=False,
                        client=request.client.host if request.client else None,
                    )
                )
                s.commit()
            raise HTTPException(500, str(e))

    @app.post("/v1/embeddings")
    async def embeddings(req: EmbeddingsReq, request: Request, _auth: str = Depends(require_auth)) -> dict[str, Any]:
        model = (req.model or settings.DEFAULT_EMBED_MODEL)
        t0 = time.time()
        try:
            decision = await app.state.policy_router.decide(model)
            vec = await decision.provider.embeddings(model=decision.model, text=req.input)

            latency = int((time.time() - t0) * 1000)
            with session() as s:
                s.add(
                    RequestLog(
                        path=str(request.url.path),
                        model=model,
                        latency_ms=latency,
                        ok=True,
                        client=request.client.host if request.client else None,
                    )
                )
                s.commit()

            return {"object": "list", "data": [{"object": "embedding", "embedding": vec, "index": 0}], "model": model}
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            with session() as s:
                s.add(
                    RequestLog(
                        path=str(request.url.path),
                        model=model,
                        latency_ms=latency,
                        ok=False,
                        client=request.client.host if request.client else None,
                    )
                )
                s.commit()
            raise HTTPException(500, str(e))

    @app.get("/v1/models")
    async def list_models(response: Response, _auth: str = Depends(require_auth)):
        try:
            data = await app.state.policy_router.list_models()
            return {"object": "list", "data": data}
        except Exception as e:
            log.exception("Failed to list models")
            response.headers["X-MatrixLLM-Warning"] = f"models_unavailable: {type(e).__name__}"
            return {"object": "list", "data": []}

    # ----------------------------
    # Admin (keep from matrixllm; still useful)
    # ----------------------------
    @app.get("/admin/recent")
    async def admin_recent(_auth: str = Depends(require_auth)):
        from sqlmodel import select
        with session() as s:
            rows = s.exec(select(RequestLog).order_by(RequestLog.ts.desc()).limit(200)).all()
            return {"recent": [r.model_dump() for r in rows]}

    @app.get("/admin/runtimes")
    async def admin_runtimes(_auth: str = Depends(require_auth)):
        nodes = await app.state.matrix.registry.list()
        return {"runtimes": [n.__dict__ for n in nodes]}

    @app.post("/admin/enroll")
    async def admin_enroll(_auth: str = Depends(require_auth)):
        tok = create_join_token()
        return {"token": tok.token, "expires_at": tok.expires_at.isoformat()}

    return app


app = create_app()
