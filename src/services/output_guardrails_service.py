"""Service handling *output* guardrail evaluation and persistence."""
from __future__ import annotations

from typing import Dict, Any, List

from sqlalchemy.orm import Session

from src.guardrails.output_guardrails import output_guardrails
from src.models.guardrails import Guardrail
from utils.tool_alignment import workflow_result_to_trace


from config import guardrail_config

def evaluate_and_store(
    db: Session,
    *,
    user_id: str,
    session_id: str,
    message_id: str,
    workflow_state: Dict[str, Any],
) -> tuple[Dict[str, Any], List[str], bool]:
    """Run output guardrails, persist, return (results, flagged_types)."""

    trace = workflow_result_to_trace(workflow_state)
    results: Dict[str, Any] = output_guardrails(trace)

    flagged: List[str] = []
    blocked = False
    out_cfg = guardrail_config.get("output_guardrails", {})
    for gtype, block in results.items():
        res = block.get("result", {}) if isinstance(block, dict) else block
        violated = any(
            (isinstance(v, bool) and v) or (isinstance(v, (int, float)) and v > 0)
            for v in res.values()
        )
        if violated:
            flagged.append(gtype)
            action = out_cfg.get(gtype, {}).get("action", "block")
            if action == "block":
                blocked = True

    # Update existing guardrail row or insert new with tool alignment results
    record = Guardrail(
        user_id=user_id,
        session_id=session_id,
        message_id=message_id,
        tool_alignment=results.get("tool_alignment"),
        code_shield=results.get("code_shield"),
    )
    db.merge(record)
    db.commit()

    return results, flagged, blocked
