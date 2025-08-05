"""FastAPI endpoint for output guardrail validation."""
from __future__ import annotations

from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.services.output_guardrails_service import evaluate_and_store

app = FastAPI(title="Output Guardrails API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OutputGuardrailRequest(BaseModel):
    user_id: str
    session_id: str
    message_id: str | None = None
    workflow_state: Dict[str, Any]  # raw state dict from agent


class OutputGuardrailResponse(BaseModel):
    results: Dict[str, Any]
    flagged_types: List[str]
    blocked: bool


@app.post("/api/output_guardrails", response_model=OutputGuardrailResponse)
async def run_output_guardrails(request: OutputGuardrailRequest, db: Session = Depends(get_db)):
    try:
        # Run potentially blocking / asyncio-incompatible code in a worker thread
        results, flagged, blocked = await asyncio.to_thread(
            evaluate_and_store,
            db,
            user_id=request.user_id,
            session_id=request.session_id,
            message_id=request.message_id or "",
            workflow_state=request.workflow_state,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OutputGuardrailResponse(results=results, flagged_types=flagged, blocked=blocked)
