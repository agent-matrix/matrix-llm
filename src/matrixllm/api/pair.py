from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from matrixllm.core.settings import settings
from matrixllm.core.pairing import pairing

router = APIRouter(tags=["pairing"])


class PairReq(BaseModel):
    code: str
    client_name: str | None = "matrixsh"


@router.get("/pair/info")
async def pair_info(request: Request):
    pm = pairing()
    info = pm.info()

    # If pairing is enabled AND local-only, refuse info to non-loopback (reduces exposure).
    client_ip = request.client.host if request.client else None
    if info.enabled and settings.PAIRING_LOCAL_ONLY and not pm.assert_pairing_local_only(client_ip):
        raise HTTPException(status_code=403, detail="Pairing is local-only")

    return {
        "pairing": info.enabled,
        "expires_in": info.expires_in,
        "local_only": info.local_only,
        "auth_mode": settings.AUTH_MODE,
    }


@router.post("/pair")
async def pair_submit(req: PairReq, request: Request):
    if settings.AUTH_MODE != "pairing":
        raise HTTPException(status_code=404, detail="Pairing not enabled")

    pm = pairing()
    client_ip = request.client.host if request.client else None
    if settings.PAIRING_LOCAL_ONLY and not pm.assert_pairing_local_only(client_ip):
        raise HTTPException(status_code=403, detail="Pairing is local-only")

    if not pm.verify_code(req.code):
        raise HTTPException(status_code=401, detail="Invalid or expired pairing code")

    token = pm.issue_token(client_name=req.client_name or "matrixsh")
    return {"token": token, "token_type": "bearer"}
