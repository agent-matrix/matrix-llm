from __future__ import annotations

from fastapi import Header, HTTPException, Request
from matrixllm.core.settings import settings
from matrixllm.core.pairing import pairing


def _keys() -> set[str]:
    return {k.strip() for k in (settings.API_KEYS or "").split(",") if k.strip()}


def _extract_bearer_or_xapikey(
    x_api_key: str | None,
    authorization: str | None,
) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def _is_loopback_ip(ip: str | None) -> bool:
    if not ip:
        return False
    return ip in ("127.0.0.1", "::1", "localhost")


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> str:
    """Backwards-compatible API key auth (original behavior)."""
    key = _extract_bearer_or_xapikey(x_api_key, authorization)
    if not key or key not in _keys():
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


def require_auth(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> str:
    """
    Unified auth dependency supporting:
      - required (default): API key required
      - local-trust: loopback allowed without key; remote requires API key
      - pairing: allow /health and /pair* (local-only by default) without key; all /v1/* require pairing token or API key
    Returns a principal string (not currently used by handlers).
    """
    mode = (settings.AUTH_MODE or "required").strip().lower()
    path = str(request.url.path)
    client_ip = request.client.host if request.client else None

    # Always allow health without auth (useful for probes)
    if path == "/health":
        return "health"

    # Mode: local-trust
    if mode == "local-trust":
        if _is_loopback_ip(client_ip):
            return "local"
        # remote: require API key
        return require_api_key(x_api_key=x_api_key, authorization=authorization)

    # Mode: pairing
    if mode == "pairing":
        pm = pairing()

        # Pairing endpoints may be unauthenticated, but optionally local-only
        if path.startswith("/pair"):
            if settings.PAIRING_LOCAL_ONLY and not pm.assert_pairing_local_only(client_ip):
                raise HTTPException(status_code=403, detail="Pairing is local-only")
            return "pairing"

        # For all other endpoints, accept either:
        # - Bearer pairing token
        # - or API key (admin override)
        token = _extract_bearer_or_xapikey(x_api_key, authorization)
        if token:
            # Accept as API key if matches configured keys
            if token in _keys():
                return "api_key"
            # Accept as pairing token if valid
            if pm.token_valid(token):
                return "pair_token"

        raise HTTPException(status_code=401, detail="Invalid or missing credentials")

    # Default: required
    return require_api_key(x_api_key=x_api_key, authorization=authorization)
