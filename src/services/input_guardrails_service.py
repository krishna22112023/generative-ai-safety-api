"""Service handling guardrail evaluation and persistence."""
from __future__ import annotations

from typing import Dict, Any

from sqlalchemy.orm import Session

from src.guardrails.input_guardrails import input_guardrails
from src.models.guardrails import Guardrail


from config import guardrail_config

def evaluate_and_store(
    db: Session,
    *,
    user_id: str,
    session_id: str,
    message_id: str,
    message: str,
) -> tuple[Dict[str, Any], list[str], bool]:

    """Run guardrails, persist, and return (results, flagged_types)."""

    results: Dict[str, Any] = input_guardrails(message)

    # Determine which guard categories are triggered & actions
    flagged: list[str] = []
    blocked = False
    input_cfg = guardrail_config.get("input_guardrails", {})

    for gtype, data in results.items():
        res_block = data.get("result", {}) if isinstance(data, dict) else data
        violated = any(
            (isinstance(v, bool) and v) or (isinstance(v, (int, float)) and v > 0)
            for v in res_block.values()
        )
        if violated:
            flagged.append(gtype)
            action = input_cfg.get(gtype, {}).get("action", "block")
            if action == "block":
                blocked = True

    record = Guardrail(
        user_id=user_id,
        session_id=session_id,
        message_id=message_id,
        toxicity=results.get("toxicity"),
        bias=results.get("bias"),
        ethics=results.get("ethics"),
        pii=results.get("pii"),
        secrets=results.get("secrets"),
        prompt_safety=results.get("prompt_safety"),
        tool_alignment=results.get("tool_alignment"),
        code_shield=results.get("code_shield"),
    )

    db.merge(record)
    db.commit()

    return results, flagged, blocked
