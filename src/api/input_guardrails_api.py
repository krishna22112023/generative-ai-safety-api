"""FastAPI application exposing *input* guardrail checks.

Flow overview
-------------
1. The **client** sends a raw prompt to this service.
2. The message is analysed by the various guardrail modules defined in
   ``src.guardrails.*``.
3. The structured results are returned to the client **and** persisted to
   ``results/<timestamp>.json`` for later inspection.

The file is completely standalone and does **not** depend on the agent
API – wiring the two pieces together is the responsibility of the caller
or a higher-level orchestration layer.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, List



from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.input_guardrails_service import evaluate_and_store

logger = logging.getLogger(__name__)

class GuardrailRequest(BaseModel):
    """Incoming request body for the guardrail endpoint."""

    user_id: str
    session_id: str
    message_id: str | None = None
    message: str = Field(..., description="User prompt to validate")


class GuardrailResponse(BaseModel):
    """Response containing guardrail report."""

    results: Dict[str, Any]
    flagged_types: List[str]
    blocked: bool

app = FastAPI(
    title="Input Guardrails API",
    description="Validate incoming user prompts against safety guardrails.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/input_guardrails", response_model=GuardrailResponse)
async def run_guardrails(request: GuardrailRequest, db: Session = Depends(get_db)):
    """Validate prompt, store results and return them."""

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message can not be empty")

    try:
        results, flagged, blocked = evaluate_and_store(
            db,
            user_id=request.user_id,
            session_id=request.session_id,
            message_id=request.message_id or "",  # type: ignore[arg-type]
            message=request.message,
        )
    except Exception as exc:
        logger.exception("Guardrail evaluation/persistence failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return GuardrailResponse(results=results, flagged_types=flagged, blocked=blocked)

