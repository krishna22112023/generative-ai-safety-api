"""Convenience launcher that starts *both* internal APIs.

Running this script starts two separate Uvicorn instances in background
threads:

1. **Input-Guardrails API**  → http://localhost:8001
2. **Agent API**             → http://localhost:8000

Feel free to run the individual entry-points under ``servers/`` if you
only need a single service during development.
"""
from __future__ import annotations

import threading
import logging

import uvicorn

from src.api.agent_api import app as _agent_app
from src.api.input_guardrails_api import app as _guardrails_app
from src.api.output_guardrails_api import app as _out_guardrails_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _run_agent() -> None:
    logger.info("Starting Agent API on http://0.0.0.0:8000 …")
    uvicorn.run(_agent_app, host="0.0.0.0", port=8000, log_level="info")


def _run_guardrails() -> None:
    logger.info("Starting Input-Guardrails API on http://0.0.0.0:8001 …")
    uvicorn.run(_guardrails_app, host="0.0.0.0", port=8001, log_level="info")

def _run_output_guardrails() -> None:
    logger.info("Starting Output-Guardrails API on http://0.0.0.0:8002 …")
    uvicorn.run(_out_guardrails_app, host="0.0.0.0", port=8002, log_level="info")


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent_thread = threading.Thread(target=_run_agent, daemon=True)
    guardrails_thread = threading.Thread(target=_run_guardrails, daemon=True)
    out_guardrails_thread = threading.Thread(target=_run_output_guardrails, daemon=True)

    agent_thread.start()
    guardrails_thread.start()
    out_guardrails_thread.start()

    agent_thread.join()
    guardrails_thread.join()
    out_guardrails_thread.join()

