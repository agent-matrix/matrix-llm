from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional

import httpx
import secrets
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from matrixllm.core.enrollment import create_join_token
from matrixllm.core.settings import settings
from matrixllm.core.pairing import pairing
from matrixllm.utils.installer import (
    ensure_model,
    ensure_ollama_server_running,
    install_ollama,
    is_ollama_installed,
)
from matrixllm.utils.process import (
    check_health,
    cleanup_stale_pid_file,
    find_process_on_port,
    read_pid_file,
    stop_process,
    write_pid_file,
)
from matrixllm.utils.tunnel import start_tunnel
from matrixllm.core.provider_config import (
    PROVIDER_INFO,
    get_configured_providers,
    get_default_model_for_provider,
    get_default_provider,
    get_provider_status,
    is_provider_configured,
    set_default_model_for_provider,
    set_default_provider,
)

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


def _get_lan_ip() -> str | None:
    """Detect LAN IP address for showing to other devices on the network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # no traffic required; just selects route
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _read_api_keys_from_dotenv() -> str | None:
    """Best-effort read of API_KEYS from a local .env file.

    We intentionally do this here (instead of only relying on Settings(env_file=".env"))
    because CLI commands may be executed from various working directories, and
    Settings is instantiated at import time.
    """
    env_path = Path(".env")
    if not env_path.exists():
        return None
    for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("API_KEYS="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _write_env_key_if_missing(key: str) -> None:
    """Write API_KEYS to .env only if missing/empty.

    This prevents overwriting a user-provided API_KEYS in .env.
    NOTE: This is only called when the user explicitly passes --write-env.
    """
    env_path = Path(".env")
    existing = env_path.read_text(encoding="utf-8", errors="ignore") if env_path.exists() else ""

    # If API_KEYS is already present and non-empty, do nothing.
    existing_key = _read_api_keys_from_dotenv()
    if existing_key and existing_key.strip():
        return

    lines: list[str] = []
    replaced = False
    for line in existing.splitlines():
        if line.strip().startswith("API_KEYS="):
            lines.append(f"API_KEYS={key}")
            replaced = True
        else:
            lines.append(line)

    if not replaced:
        if existing.strip():
            lines.append("")
        lines.append(f"API_KEYS={key}")

    env_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _dashboard(host: str, port: int, public_url: str | None, key: str, model: str, workers: int, join_token: str, auth_mode: str = "required", pairing_code: str | None = None):
    local_url = f"http://localhost:{port}"

    if auth_mode == "pairing":
        msg = f"""
[bold green]✅ MatrixLLM is Online[/bold green]

[bold]Model:[/bold]        {model}
[bold]Workers:[/bold]      {workers}
[bold]Local API:[/bold]    {local_url}/v1
[bold]Health:[/bold]       {local_url}/health
[bold]Auth:[/bold]         pairing
[bold]Pairing code:[/bold]  {pairing_code}
[dim]Enter this code in MatrixShell to pair (code expires soon).[/dim]

[bold]Node join token:[/bold]  {join_token}
[dim]Example node command:[/dim]
[dim]  matrixllm-node join --control {local_url} --token {join_token}[/dim]
"""
    else:
        msg = f"""
[bold green]✅ MatrixLLM is Online[/bold green]

[bold]Model:[/bold]        {model}
[bold]Workers:[/bold]      {workers}
[bold]Local API:[/bold]    {local_url}/v1
[bold]Health:[/bold]       {local_url}/health
[bold]Key:[/bold]          {key}
[dim]Send as X-API-Key or Authorization: Bearer ...[/dim]

[bold]Node join token:[/bold]  {join_token}
[dim]Example node command:[/dim]
[dim]  matrixllm-node join --control {local_url} --token {join_token}[/dim]

[bold cyan]Ollabridge compatible:[/bold cyan]
[dim]  OLLAS_BASE_URL={local_url}/v1[/dim]
[dim]  OLLAS_API_KEY={key}[/dim]
[dim]  OLLAS_MODEL={model}[/dim]
"""

    if public_url:
        msg += f"""
[bold yellow]🌍 Public URL:[/bold yellow]   [link={public_url}]{public_url}[/link]
[dim]Use {public_url}/v1 as your OpenAI base_url[/dim]
"""

    console.print(Panel(msg, title="🚀 Gateway Ready", border_style="blue"))


@app.command()
def start(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(11435, help="Bind port"),
    auth: str = typer.Option("required", "--auth", help="Auth mode: required|local-trust|pairing"),
    share: bool = typer.Option(False, "--share", help="Expose a public URL (best-effort)"),
    lan: bool = typer.Option(False, "--lan", help="Print LAN URL for other devices"),
    workers: int = typer.Option(1, "--workers", help="Worker processes (scalability hook)"),
    model: str = typer.Option("deepseek-r1", "--model", help="Default chat model to ensure/use"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes (dev mode)"),
    log_level: str = typer.Option(
        "warning",
        "--log-level",
        help="Uvicorn log level (debug, info, warning, error, critical)",
    ),
    write_env: bool = typer.Option(
        False,
        "--write-env",
        help="If API_KEYS is missing, write a generated key to .env (off by default for safety).",
    ),
    replace: bool = typer.Option(
        False,
        "--replace",
        help="If an instance is already running on this port, stop it first and start a new one.",
    ),
    pid_file: Optional[str] = typer.Option(
        None,
        "--pid-file",
        help="Path to pid/metadata file (advanced).",
    ),
):
    """🚀 Start MatrixLLM (self-healing: installs Ollama + pulls model)."""

    # 0) Handle --replace: stop any existing instance on this port
    if replace:
        existing = find_process_on_port(port)
        if existing:
            console.print(f"[yellow]⚠️  Stopping existing instance on port {port} (PID {existing})...[/yellow]")
            success, msg = stop_process(port=port, timeout=8.0, force=True)
            if success:
                console.print(f"[green]✓[/green] {msg}")
            else:
                console.print(f"[red]✗[/red] {msg}")
                raise typer.Exit(1)
    else:
        # Check if port is already in use
        existing = find_process_on_port(port)
        if existing:
            console.print(f"[red]✗ Port {port} is already in use (PID {existing}).[/red]")
            console.print("[dim]Use --replace to stop the existing instance first.[/dim]")
            raise typer.Exit(1)

    # Clean up stale PID files
    cleanup_stale_pid_file(port)

    # 1) Self-healing: install Ollama
    if not is_ollama_installed():
        install_ollama()

    # 2) Start Ollama server (best effort)
    ensure_ollama_server_running()

    # 3) Ensure model exists
    ensure_model(model)

    # 4) Auth precedence:
    #    - Prefer env var API_KEYS
    #    - Then OLLAS_API_KEY (ollabridge compatibility)
    #    - Then .env (best-effort)
    #    - Then settings.API_KEYS (last resort; may have been instantiated before .env is read)
    configured_keys = (os.getenv("API_KEYS") or "").strip()
    if not configured_keys:
        configured_keys = (os.getenv("OLLAS_API_KEY") or "").strip()  # ollabridge compat
    if not configured_keys:
        configured_keys = (_read_api_keys_from_dotenv() or "").strip()
    if not configured_keys:
        configured_keys = (settings.API_KEYS or "").strip()

    key = (configured_keys.split(",")[0].strip() if configured_keys else "")

    # Treat common defaults as "not configured"
    if (not key) or ("change-me" in key) or ("dev-key" in key):
        # Generate a per-run secret key (not persisted unless --write-env is passed)
        key = f"sk-matrixllm-{secrets.token_urlsafe(18)}"
        configured_keys = key
        if write_env:
            _write_env_key_if_missing(key)

    # Ensure the running process + singleton settings see the effective key
    os.environ["API_KEYS"] = configured_keys
    settings.API_KEYS = configured_keys

    # Auth mode (default is required; keeps current behavior)
    os.environ["AUTH_MODE"] = auth
    settings.AUTH_MODE = auth

    pairing_code = None
    if auth == "pairing":
        # Generate a short pairing code on startup
        pairing_code = pairing().reset_pair_code()
        if host not in ("127.0.0.1", "localhost"):
            console.print("[yellow]Warning: Pairing mode is intended for localhost only. Consider --host 127.0.0.1[/yellow]")

    # 5) Enrollment token: compute nodes join the control plane with this short-lived credential.
    join_token = create_join_token().token

    # 6) Optional public access URL
    public_url = None
    if share:
        console.print("[green]🌍 Opening tunnel to public internet...[/green]")
        try:
            public_url = start_tunnel(port)
        except Exception as e:
            console.print(f"[red]Public link failed:[/red] {e}")
            console.print("[yellow]Tip:[/yellow] For production, use a managed edge or private overlay.")

    # Dev convenience: Uvicorn reload cannot be combined with multiple workers
    if reload and workers != 1:
        console.print("[yellow]⚠️  --reload forces --workers 1 (Uvicorn limitation).[/yellow]")
        workers = 1

    _dashboard(host, port, public_url, key, model, workers, join_token, auth, pairing_code)

    # Write PID file for process management
    write_pid_file(
        port=port,
        host=host,
        model=model,
        auth_mode=auth,
        api_key=key,
        custom_path=pid_file,
    )

    # LAN mode: print URLs for other devices on the network
    if lan:
        lan_ip = _get_lan_ip()
        if lan_ip:
            console.print()
            console.print("[bold cyan]🌐 LAN Access[/bold cyan]")
            console.print(f"[bold]LAN API base:[/bold]    http://{lan_ip}:{port}/v1")
            console.print(f"[bold]LAN Health:[/bold]      http://{lan_ip}:{port}/health")
            console.print()
            console.print("[bold]Example (with API key):[/bold]")
            console.print(f"curl -H 'Authorization: Bearer <API_KEY>' http://{lan_ip}:{port}/v1/models")
            console.print()
        else:
            console.print("[yellow]⚠️  Could not detect LAN IP address[/yellow]")

    uvicorn.run(
        "matrixllm.api.main:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        reload=reload,
    )


@app.command()
def enroll_create(
    ttl_seconds: int = typer.Option(3600, "--ttl", help="Token TTL in seconds"),
):
    """Create a short-lived enrollment token for nodes to join the Control Plane."""
    tok = create_join_token(ttl_seconds=ttl_seconds)
    console.print(
        Panel(
            f"[bold]Token:[/bold] {tok.token}\n[bold]Expires:[/bold] {tok.expires_at.isoformat()}",
            title="🔑 Enrollment Token",
        )
    )


@app.command()
def up(
    share: bool = typer.Option(False, "--share", help="Alias of `start --share` (backwards compatible)."),
):
    """Backwards-compatible alias for older docs."""
    start(share=share)


@app.command()
def doctor(
    port: int = typer.Option(11435, help="MatrixLLM port"),
    ollama_base: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
):
    """🩺 Diagnose local setup (Ollama, MatrixLLM, auth, CORS)."""
    table = Table(title="MatrixLLM Doctor")
    table.add_column("Check")
    table.add_column("Result")

    # Ollama reachable?
    try:
        r = httpx.get(f"{ollama_base}/api/tags", timeout=3)
        table.add_row("Ollama /api/tags", "✅ OK" if r.status_code == 200 else f"❌ HTTP {r.status_code}")
    except Exception as e:
        table.add_row("Ollama /api/tags", f"❌ {type(e).__name__}")

    # MatrixLLM health (no auth required)
    try:
        r = httpx.get(f"http://localhost:{port}/health", timeout=3)
        table.add_row("MatrixLLM /health", "✅ OK" if r.status_code == 200 else f"❌ HTTP {r.status_code}")
    except Exception as e:
        table.add_row("MatrixLLM /health", f"❌ {type(e).__name__}")

    # Auth + CORS config visibility
    table.add_row("API_KEYS configured", "✅ yes" if settings.API_KEYS else "❌ missing")
    table.add_row("CORS_ORIGINS", settings.CORS_ORIGINS or "(disabled)")

    # Show how to call with key
    table.add_row("Auth usage", "Use Authorization: Bearer <key> or X-API-Key: <key>")

    console.print(table)


@app.command()
def models(
    port: int = typer.Option(11435, help="MatrixLLM port"),
    api_key: str = typer.Option(..., help="API key (required)"),
):
    """📦 List available models via MatrixLLM (requires API key)."""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = httpx.get(f"http://localhost:{port}/v1/models", headers=headers, timeout=15)
        r.raise_for_status()

        warn = r.headers.get("X-MatrixLLM-Warning")
        if warn:
            console.print(f"[yellow]Warning:[/yellow] {warn}")

        data = r.json()
        for m in data.get("data", []):
            console.print(m.get("id"))
    except httpx.HTTPStatusError as e:
        console.print(f"[red]HTTP Error {e.response.status_code}:[/red] {e.response.text}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("test-chat")
def test_chat(
    prompt: str = typer.Argument("Say hello in one sentence."),
    port: int = typer.Option(11435, help="MatrixLLM port"),
    model: str = typer.Option("", help="Model id (optional)"),
    api_key: str = typer.Option(..., help="API key (required)"),
):
    """💬 Send a test chat completion to MatrixLLM (requires API key)."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model or None,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        r = httpx.post(f"http://localhost:{port}/v1/chat/completions", headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        msg = j["choices"][0]["message"]["content"]
        console.print(Panel(msg, title="Assistant"))
    except httpx.HTTPStatusError as e:
        console.print(f"[red]HTTP Error {e.response.status_code}:[/red] {e.response.text}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status(
    port: int = typer.Option(11435, help="Port to check"),
    host: str = typer.Option("127.0.0.1", help="Host to check"),
    json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
):
    """📡 Show status of a running MatrixLLM instance (pid/port/model/health)."""
    health = check_health(host=host, port=port)

    if json_output:
        console.print(json.dumps(health, indent=2))
        return

    if health["running"] or health["healthy"]:
        console.print("[bold green]✅ running[/bold green]")
        if health["pid"]:
            console.print(f"[bold]PID:[/bold]     {health['pid']}")
        console.print(f"[bold]URL:[/bold]     {health['url']}")
        console.print(f"[bold]API:[/bold]     {health['api_url']}")
        if health["model"]:
            console.print(f"[bold]Model:[/bold]   {health['model']}")
        if health["auth_mode"]:
            console.print(f"[bold]Auth:[/bold]    {health['auth_mode']}")
        console.print(f"[bold]Health:[/bold]  {'OK' if health['healthy'] else 'DEGRADED'}")
    else:
        console.print("[bold red]❌ not running[/bold red]")
        if health["error"]:
            console.print(f"[dim]Error: {health['error']}[/dim]")
        raise typer.Exit(1)


@app.command()
def stop(
    port: int = typer.Option(11435, help="Which instance to stop"),
    host: str = typer.Option("127.0.0.1", help="Host"),
    timeout: float = typer.Option(8.0, help="Seconds to wait for graceful shutdown"),
    force: bool = typer.Option(False, "--force", help="If still running after timeout, send a hard kill (SIGKILL)."),
):
    """🛑 Stop a running MatrixLLM instance (graceful by default)."""
    console.print(f"[yellow]Stopping MatrixLLM on port {port}...[/yellow]")

    success, msg = stop_process(port=port, host=host, timeout=timeout, force=force)

    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        console.print(f"[red]✗[/red] {msg}")
        raise typer.Exit(1)


@app.command()
def restart(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(11435, help="Bind port"),
    auth: str = typer.Option("required", "--auth", help="Auth mode: required|local-trust|pairing"),
    workers: int = typer.Option(1, "--workers", help="Worker processes"),
    model: str = typer.Option("deepseek-r1", "--model", help="Default chat model to ensure/use"),
    log_level: str = typer.Option("warning", "--log-level", help="Uvicorn log level"),
    timeout: float = typer.Option(8.0, help="Stop timeout seconds"),
    force: bool = typer.Option(False, "--force", help="Force kill if needed"),
):
    """🔁 Restart MatrixLLM (stop + start, optionally change model/port/auth)."""
    # Stop existing instance
    console.print(f"[yellow]Stopping existing instance on port {port}...[/yellow]")
    success, msg = stop_process(port=port, timeout=timeout, force=force)
    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        # Only fail if there was an actual error (not just "no instance running")
        if "No instance running" not in msg:
            console.print(f"[red]✗[/red] {msg}")
            raise typer.Exit(1)
        console.print(f"[dim]{msg}[/dim]")

    console.print()
    console.print("[green]Starting MatrixLLM...[/green]")

    # Start new instance using subprocess to avoid blocking
    cmd = [
        sys.executable, "-m", "matrixllm.cli.main", "start",
        "--host", host,
        "--port", str(port),
        "--auth", auth,
        "--workers", str(workers),
        "--model", model,
        "--log-level", log_level,
    ]

    # Replace current process with the new start command
    os.execv(sys.executable, cmd)


@app.command()
def use(
    model: str = typer.Argument(..., help="The Ollama model name, e.g. llama3.1:8b, qwen2.5:7b, deepseek-r1:7b"),
    port: int = typer.Option(11435, help="Which instance to restart"),
    host: str = typer.Option("127.0.0.1", help="Host"),
    timeout: float = typer.Option(8.0, help="Stop timeout seconds"),
    force: bool = typer.Option(False, "--force", help="Force kill if needed"),
):
    """🎛 Switch the default model (restart safely with a new --model)."""
    console.print(f"[cyan]Switching to model: {model}[/cyan]")

    # Read current config from PID file if available
    info = read_pid_file(port)
    current_host = "0.0.0.0"
    current_auth = "required"
    current_workers = 1
    current_log_level = "warning"

    if info:
        current_host = info.host
        current_auth = info.auth_mode
        console.print(f"[dim]Current instance: PID {info.pid}, model {info.model}[/dim]")

    # Stop existing instance
    console.print(f"[yellow]Stopping existing instance...[/yellow]")
    success, msg = stop_process(port=port, host=host, timeout=timeout, force=force)
    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        if "No instance running" not in msg:
            console.print(f"[red]✗[/red] {msg}")
            raise typer.Exit(1)
        console.print(f"[dim]{msg}[/dim]")

    console.print()
    console.print(f"[green]Starting MatrixLLM with model {model}...[/green]")

    # Start new instance with the new model
    cmd = [
        sys.executable, "-m", "matrixllm.cli.main", "start",
        "--host", current_host,
        "--port", str(port),
        "--auth", current_auth,
        "--model", model,
        "--log-level", current_log_level,
    ]

    # Replace current process with the new start command
    os.execv(sys.executable, cmd)


@app.command()
def providers(
    json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
):
    """🔌 List available LLM providers and their configuration status."""
    status_info = get_provider_status()
    default = get_default_provider()

    if json_output:
        output = {
            "default_provider": default,
            "providers": status_info,
        }
        console.print(json.dumps(output, indent=2))
        return

    console.print()
    console.print("[bold]LLM Providers[/bold]")
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Provider", style="cyan")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Model Prefix")

    for provider, info in status_info.items():
        is_default = provider == default
        configured = info["configured"]

        # Status indicator
        if configured:
            status_str = "[green]✓ configured[/green]"
            if is_default:
                status_str += " [yellow](default)[/yellow]"
        else:
            missing = ", ".join(info["missing_vars"]) if info["missing_vars"] else "N/A"
            status_str = f"[dim]✗ missing: {missing}[/dim]"

        # Provider name with default indicator
        name = info["name"]
        if is_default:
            name = f"[bold]{name}[/bold]"

        prefix = info["model_prefix"] or "(none)"

        table.add_row(name, status_str, info["description"], prefix)

    console.print(table)
    console.print()

    # Show example usage
    configured = get_configured_providers()
    if configured:
        console.print("[bold]Quick start:[/bold]")
        console.print(f"  matrixllm provider use <provider>   # Set default provider")
        console.print(f"  matrixllm provider models <provider> # Show example models")
        console.print()
        console.print("[bold]Configured providers:[/bold]", ", ".join(configured))


@app.command("provider")
def provider_cmd(
    action: str = typer.Argument(..., help="Action: use, models, info"),
    provider: str = typer.Argument(None, help="Provider name (ollama, openai, anthropic, google, watsonx)"),
    model: str = typer.Option(None, "--model", help="Set default model for provider"),
):
    """🔌 Manage LLM providers (use, models, info)."""
    if action == "use":
        if not provider:
            console.print("[red]Error: provider name required[/red]")
            console.print("Usage: matrixllm provider use <provider>")
            console.print(f"Available: {', '.join(PROVIDER_INFO.keys())}")
            raise typer.Exit(1)

        success, msg = set_default_provider(provider)
        if success:
            console.print(f"[green]✓[/green] {msg}")

            # Also set default model if provided
            if model:
                success2, msg2 = set_default_model_for_provider(provider, model)
                if success2:
                    console.print(f"[green]✓[/green] {msg2}")
                else:
                    console.print(f"[yellow]⚠️[/yellow] {msg2}")

            # Show how to use the provider
            info = PROVIDER_INFO.get(provider, {})
            prefix = info.get("model_prefix", "")
            example_models = info.get("example_models", [])
            if example_models:
                console.print()
                console.print("[bold]Example usage:[/bold]")
                console.print(f"  matrixllm test-chat 'Hello' --model {example_models[0]} --api-key YOUR_KEY")
        else:
            console.print(f"[red]✗[/red] {msg}")
            raise typer.Exit(1)

    elif action == "models":
        if not provider:
            # Show all providers with their models
            console.print()
            for p, info in PROVIDER_INFO.items():
                configured = is_provider_configured(p)
                status = "[green]✓[/green]" if configured else "[dim]✗[/dim]"
                console.print(f"{status} [bold]{info['name']}[/bold] ({p})")
                for m in info.get("example_models", []):
                    console.print(f"    {m}")
                console.print()
        else:
            if provider not in PROVIDER_INFO:
                console.print(f"[red]Unknown provider: {provider}[/red]")
                console.print(f"Available: {', '.join(PROVIDER_INFO.keys())}")
                raise typer.Exit(1)

            info = PROVIDER_INFO[provider]
            configured = is_provider_configured(provider)
            status = "[green]configured[/green]" if configured else "[red]not configured[/red]"

            console.print()
            console.print(f"[bold]{info['name']}[/bold] ({status})")
            console.print(f"[dim]{info['description']}[/dim]")
            console.print()
            console.print("[bold]Example models:[/bold]")
            for m in info.get("example_models", []):
                console.print(f"  {m}")

            if not configured:
                console.print()
                console.print("[bold]Required environment variables:[/bold]")
                for var in info.get("required_vars", []):
                    console.print(f"  {var}")

    elif action == "info":
        if not provider:
            console.print("[red]Error: provider name required[/red]")
            raise typer.Exit(1)

        if provider not in PROVIDER_INFO:
            console.print(f"[red]Unknown provider: {provider}[/red]")
            raise typer.Exit(1)

        info = PROVIDER_INFO[provider]
        configured = is_provider_configured(provider)

        console.print()
        console.print(f"[bold]{info['name']}[/bold]")
        console.print(f"[dim]{info['description']}[/dim]")
        console.print()
        console.print(f"[bold]Status:[/bold] {'[green]configured[/green]' if configured else '[red]not configured[/red]'}")
        console.print(f"[bold]Model prefix:[/bold] {info.get('model_prefix') or '(none)'}")
        console.print()

        console.print("[bold]Environment variables:[/bold]")
        for var in info.get("env_vars", []):
            required = var in info.get("required_vars", [])
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                masked = value[:8] + "..." if len(value) > 12 else value
                console.print(f"  {var}: [green]{masked}[/green]")
            elif required:
                console.print(f"  {var}: [red]NOT SET (required)[/red]")
            else:
                console.print(f"  {var}: [dim]not set[/dim]")

        console.print()
        console.print("[bold]Example models:[/bold]")
        for m in info.get("example_models", []):
            console.print(f"  {m}")

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: use, models, info")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
