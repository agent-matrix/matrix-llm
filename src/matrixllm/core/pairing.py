from __future__ import annotations

import json
import secrets
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from matrixllm.core.settings import settings


def _now() -> int:
    return int(time.time())


def _is_loopback_ip(ip: str | None) -> bool:
    if not ip:
        return False
    return ip in ("127.0.0.1", "::1", "localhost")


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


@dataclass
class PairInfo:
    enabled: bool
    expires_in: int
    local_only: bool


class PairingManager:
    """
    Minimal pairing manager:
      - generates short pairing codes with TTL
      - mints long-lived tokens
      - stores tokens hashed in ~/.matrixllm/pair_tokens.json
    """

    def __init__(self, tokens_file: Path):
        self.tokens_file = tokens_file
        self._pair_code: str | None = None
        self._pair_exp: int = 0
        self._tokens: dict[str, dict] = {}  # token_hash -> meta
        self._load_tokens()

    def _load_tokens(self) -> None:
        try:
            if self.tokens_file.exists():
                obj = json.loads(self.tokens_file.read_text(encoding="utf-8"))
                if isinstance(obj, dict):
                    self._tokens = obj
        except Exception:
            self._tokens = {}

    def _save_tokens(self) -> None:
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.tokens_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._tokens, indent=2), encoding="utf-8")
        tmp.replace(self.tokens_file)

    def reset_pair_code(self) -> str:
        # Code format: 6 digits, displayed as XXX-XXX
        n = secrets.randbelow(1_000_000)
        code = f"{n:06d}"
        code = f"{code[:3]}-{code[3:]}"
        ttl = int(getattr(settings, "PAIRING_CODE_TTL_SECONDS", 120))
        self._pair_code = code
        self._pair_exp = _now() + max(30, ttl)
        return code

    def info(self) -> PairInfo:
        if settings.AUTH_MODE != "pairing":
            return PairInfo(enabled=False, expires_in=0, local_only=bool(settings.PAIRING_LOCAL_ONLY))
        expires_in = max(0, self._pair_exp - _now()) if self._pair_code else 0
        return PairInfo(enabled=True, expires_in=expires_in, local_only=bool(settings.PAIRING_LOCAL_ONLY))

    def verify_code(self, code: str) -> bool:
        if settings.AUTH_MODE != "pairing":
            return False
        if not self._pair_code:
            return False
        if _now() > self._pair_exp:
            return False
        return code.strip() == self._pair_code

    def issue_token(self, *, client_name: str = "matrixsh") -> str:
        # Long-lived token
        token = f"mtx_{secrets.token_urlsafe(32)}"
        th = _sha256(token)
        self._tokens[th] = {
            "client": client_name,
            "created_at": _now(),
            "last_used_at": _now(),
            "revoked": False,
        }
        self._save_tokens()
        return token

    def token_valid(self, token: str) -> bool:
        th = _sha256(token)
        meta = self._tokens.get(th)
        if not meta:
            return False
        if meta.get("revoked"):
            return False
        meta["last_used_at"] = _now()
        # Save lazily (optional). We save immediately for simplicity.
        self._save_tokens()
        return True

    def assert_pairing_local_only(self, client_ip: str | None) -> bool:
        # If PAIRING_LOCAL_ONLY: only accept pairing requests from loopback.
        if not settings.PAIRING_LOCAL_ONLY:
            return True
        return _is_loopback_ip(client_ip)


_pairing_singleton: PairingManager | None = None


def pairing() -> PairingManager:
    global _pairing_singleton
    if _pairing_singleton is None:
        _pairing_singleton = PairingManager(tokens_file=settings.PAIRING_TOKENS_FILE)
    return _pairing_singleton
