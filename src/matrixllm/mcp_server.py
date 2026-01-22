"""Backwards-compatible MCP entrypoint.

The MCP implementation moved to :mod:`matrixllm.mcp.server`.
"""

from __future__ import annotations

from matrixllm.mcp.server import main


if __name__ == "__main__":
    main()
