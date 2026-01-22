from __future__ import annotations

from dataclasses import dataclass

from matrixllm.connectors.direct_endpoint import DirectEndpointConnector
from matrixllm.core.registry import RuntimeRegistry
from matrixllm.core.router import Router


@dataclass
class AppState:
    registry: RuntimeRegistry
    router: Router
    direct: DirectEndpointConnector


def build_state() -> AppState:
    registry = RuntimeRegistry()
    router = Router(registry)
    return AppState(registry=registry, router=router, direct=DirectEndpointConnector())
