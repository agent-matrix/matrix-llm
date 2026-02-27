"""Process management utilities for MatrixLLM daemon control.

Handles PID file tracking, process detection, and graceful shutdown.
"""
from __future__ import annotations

import json
import os
import signal
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

from matrixllm.core.settings import settings


@dataclass
class ProcessInfo:
    """Metadata about a running MatrixLLM instance."""
    pid: int
    port: int
    host: str
    model: str
    auth_mode: str
    started_at: str
    api_key: Optional[str] = None  # First key (masked for display)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProcessInfo":
        return cls(**data)


def get_pid_file_path(port: int = 11435, custom_path: Optional[str] = None) -> Path:
    """Get the path to the PID file for a given port."""
    if custom_path:
        return Path(custom_path)
    return settings.DATA_DIR / f"matrixllm-{port}.pid"


def write_pid_file(
    port: int,
    host: str,
    model: str,
    auth_mode: str,
    api_key: Optional[str] = None,
    custom_path: Optional[str] = None,
) -> Path:
    """Write process info to PID file."""
    pid_path = get_pid_file_path(port, custom_path)
    pid_path.parent.mkdir(parents=True, exist_ok=True)

    info = ProcessInfo(
        pid=os.getpid(),
        port=port,
        host=host,
        model=model,
        auth_mode=auth_mode,
        started_at=datetime.utcnow().isoformat(),
        api_key=_mask_key(api_key) if api_key else None,
    )

    pid_path.write_text(json.dumps(info.to_dict(), indent=2))
    return pid_path


def read_pid_file(port: int = 11435, custom_path: Optional[str] = None) -> Optional[ProcessInfo]:
    """Read process info from PID file."""
    pid_path = get_pid_file_path(port, custom_path)
    if not pid_path.exists():
        return None
    try:
        data = json.loads(pid_path.read_text())
        return ProcessInfo.from_dict(data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def remove_pid_file(port: int = 11435, custom_path: Optional[str] = None) -> None:
    """Remove the PID file."""
    pid_path = get_pid_file_path(port, custom_path)
    if pid_path.exists():
        pid_path.unlink()


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
        return True
    except OSError:
        return False


def _mask_key(key: str) -> str:
    """Mask an API key for display (show first 8 chars + ...)."""
    if not key or len(key) <= 12:
        return key
    return key[:8] + "..." + key[-4:]


def check_health(host: str = "127.0.0.1", port: int = 11435, timeout: float = 3.0) -> dict:
    """Check health of a running MatrixLLM instance.

    Returns a dict with status information.
    """
    result = {
        "running": False,
        "healthy": False,
        "pid": None,
        "port": port,
        "host": host,
        "url": f"http://{host}:{port}",
        "api_url": f"http://{host}:{port}/v1",
        "model": None,
        "auth_mode": None,
        "error": None,
    }

    # Try to read PID file first
    info = read_pid_file(port)
    if info:
        result["pid"] = info.pid
        result["model"] = info.model
        result["auth_mode"] = info.auth_mode
        if is_process_running(info.pid):
            result["running"] = True

    # Check HTTP health endpoint
    try:
        r = httpx.get(f"http://{host}:{port}/health", timeout=timeout)
        if r.status_code == 200:
            result["healthy"] = True
            result["running"] = True
            # Try to get more info from health response
            try:
                health_data = r.json()
                if "model" in health_data:
                    result["model"] = health_data["model"]
            except Exception:
                pass
    except httpx.ConnectError:
        result["error"] = "Connection refused"
    except httpx.TimeoutException:
        result["error"] = "Connection timeout"
    except Exception as e:
        result["error"] = str(e)

    return result


def find_process_on_port(port: int) -> Optional[int]:
    """Find the PID of a process listening on the given port.

    Uses multiple methods to find the process:
    1. PID file
    2. lsof (Unix)
    3. ss (Linux)
    """
    # Method 1: PID file
    info = read_pid_file(port)
    if info and is_process_running(info.pid):
        return info.pid

    # Method 2: lsof (Unix/macOS)
    try:
        import subprocess
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            if pids:
                return int(pids[0])
    except Exception:
        pass

    # Method 3: ss (Linux)
    try:
        import subprocess
        result = subprocess.run(
            ["ss", "-tlnp", f"sport = :{port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # Parse ss output to find PID
            for line in result.stdout.split("\n"):
                if f":{port}" in line:
                    # Look for pid=XXXX pattern
                    import re
                    match = re.search(r'pid=(\d+)', line)
                    if match:
                        return int(match.group(1))
    except Exception:
        pass

    return None


def stop_process(
    port: int = 11435,
    host: str = "127.0.0.1",
    timeout: float = 8.0,
    force: bool = False,
) -> tuple[bool, str]:
    """Stop a running MatrixLLM instance.

    Args:
        port: Port the instance is running on
        host: Host (for health check)
        timeout: Seconds to wait for graceful shutdown
        force: If True, send SIGKILL after timeout

    Returns:
        Tuple of (success, message)
    """
    # Find the process
    pid = find_process_on_port(port)
    if not pid:
        # Check if anything is actually running via health check
        health = check_health(host, port)
        if not health["running"] and not health["healthy"]:
            return True, "No instance running on this port"
        return False, "Could not find process PID"

    # Try graceful shutdown (SIGTERM)
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as e:
        return False, f"Failed to send SIGTERM: {e}"

    # Wait for process to exit
    start = time.time()
    while time.time() - start < timeout:
        if not is_process_running(pid):
            remove_pid_file(port)
            return True, f"Stopped gracefully (PID {pid})"
        time.sleep(0.25)

    # Process still running after timeout
    if force:
        try:
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
            if not is_process_running(pid):
                remove_pid_file(port)
                return True, f"Force killed (PID {pid})"
            return False, f"SIGKILL sent but process still running (PID {pid})"
        except OSError as e:
            return False, f"Failed to send SIGKILL: {e}"

    return False, f"Process still running after {timeout}s timeout (PID {pid}). Use --force to kill."


def cleanup_stale_pid_file(port: int = 11435) -> bool:
    """Remove PID file if the process is no longer running.

    Returns True if a stale file was cleaned up.
    """
    info = read_pid_file(port)
    if info and not is_process_running(info.pid):
        remove_pid_file(port)
        return True
    return False
