from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from src.schema.guardrails import GuardrailCreate


router = APIRouter(prefix="/guardrails_v1",tags=["guardrails"])


@router.post("/", summary="Send accept/reject/human-in-the-loop-required messages from a guardrail result",
             description="This endpoint is used to send accept/reject/human-in-the-loop-required messages from a guardrail result")
async def generate_guardrail_result(payload: GuardrailCreate) -> Dict[str, Any]:
    """Persist a single guardrail evaluation result.
    """
    data: Dict[str, Any] = payload.model_dump(exclude_unset=True)

    # Map field names that differ between the pydantic schema and the SQL model
    model_explainability = data.pop("model_explainability", None)
    if model_explainability is not None:
        data["confidence_score"] = model_explainability

    # Auto-fill timestamp when not provided
    data.setdefault("timestamp", datetime.utcnow())

    db_obj = Guardrail(**data)
    db.add(db_obj)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_obj)

    # Return the newly created record as JSON (leveraging SQLAlchemy row → dict)
    # We avoid exposing internal SQLAlchemy state by converting explicitly.
    response = {
        "user_id": db_obj.user_id,
        "session_id": db_obj.session_id,
        "message_id": db_obj.message_id,
        "timestamp": db_obj.timestamp,
        "toxicity": db_obj.toxicity,
        "bias": db_obj.bias,
        "privacy": db_obj.privacy,
        "prompt_attack": db_obj.prompt_attack,
        "topic_relevance": db_obj.topic_relevance,
        "alignment": db_obj.alignment,
        "code_safety": db_obj.code_safety,
        "formatting": db_obj.formatting,
        "confidence_score": db_obj.confidence_score,
    }
    return response



