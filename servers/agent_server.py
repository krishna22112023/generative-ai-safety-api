"""Entry-point for running the **Agent API** service.

Example
-------
$ python -m servers.agent_server --port 8000
"""
from __future__ import annotations

import argparse
import uvicorn

from src.api.agent_api import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Agent API server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, log_level="info")


if __name__ == "__main__":
    main()
