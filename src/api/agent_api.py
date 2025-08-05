"""FastAPI application exposing the agent workflow.
"""

from __future__ import annotations

import asyncio
import json
import httpx
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage

from sqlalchemy.orm import Session

from src.agents.workflow import run_agent_workflow
from src.db.session import get_db
from src.services.chat_service import process_chat
from src.schema.chat import ChatMessage, ChatRequest

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent API",
    description="Simple wrapper around the LangGraph agent workflow",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _chatmessage_to_lc(msg: ChatMessage) -> BaseMessage:
    """Convert ChatMessage to LangChain message (simple version)."""
    return HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)


async def _invoke_agent(latest_user_input: str) -> Dict[str, Any]:
    """Invoke the synchronous agent helper in a background thread."""

    try:
        result = await asyncio.to_thread(run_agent_workflow, user_input=latest_user_input)
    except Exception as exc:  # pragma: no cover – surface internal errors
        logger.exception("Agent execution failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result



@app.post("/api/agent/chat", summary="Non-streaming chat endpoint")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Validate request, invoke agent through service layer and persist the result."""

    if not request.messages:
        raise HTTPException(status_code=400, detail="`messages` cannot be empty")

    # ------------------------------------------------------------------
    # 1) Guardrail check via separate service
    # ------------------------------------------------------------------
    latest_user_content = request.messages[-1].content
    guardrail_payload = {
        "user_id": request.user_id,
        "session_id": request.session_id,
        "message_id": "msg_" + request.session_id,
        "message": latest_user_content,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            gr_resp = await client.post("http://127.0.0.1:8001/api/input_guardrails", json=guardrail_payload)
            gr_resp.raise_for_status()
            gr_json = gr_resp.json()
    except httpx.HTTPError as exc:
        logger.error("Guardrail service unavailable: %s", exc)
        raise HTTPException(status_code=502, detail="Guardrail service unavailable") from exc

    if gr_json.get("blocked"):
        guard_types_str = ", ".join(gr_json["flagged_types"])
        content = f"{guard_types_str} detected! I’m here to provide respectful and constructive help. If you have a question or need support, I’m happy to assist :)"
        return {"messages": [{"role": "assistant", "content": content}]}
    # If action is noop or hitl allow to continue (hitl TODO)

    # ------------------------------------------------------------------
    # 2) Normal agent processing when safe
    # ------------------------------------------------------------------
    try:
        agent_state = await asyncio.to_thread(process_chat, db, request)
    except Exception as exc:
        logger.exception("Processing chat failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ------------------------------------------------------------------
    # 3) If ToolMessage present, run OUTPUT guardrails
    # ------------------------------------------------------------------
    tool_present = any(isinstance(m, ToolMessage) for m in agent_state.get("messages", []))
    if tool_present:
        # Convert messages into a JSON-serialisable format before sending over HTTP
        def _msg_to_dict(m: BaseMessage):
            if isinstance(m, AIMessage):
                role = "assistant"
            elif isinstance(m, HumanMessage):
                role = "user"
            elif isinstance(m, ToolMessage):
                role = "tool"
            else:
                role = "system"
            return {"role": role, "content": m.content}

        safe_state = {
            **agent_state,
            "messages": [_msg_to_dict(m) for m in agent_state.get("messages", [])],
        }

        og_payload = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message_id": "msg_" + request.session_id,
            "workflow_state": safe_state,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                og_resp = await client.post("http://127.0.0.1:8002/api/output_guardrails", json=og_payload)
                og_resp.raise_for_status()
                og_json = og_resp.json()
        except httpx.HTTPError as exc:
            logger.error("Output guardrail service unavailable: %s", exc)
            raise HTTPException(status_code=502, detail="Output guardrail service unavailable") from exc

        if og_json.get("blocked"):
            guard_types_str = ", ".join(og_json["flagged_types"])
            content = f"{guard_types_str} detected! I’m here to provide respectful and constructive help. If you have a question or need support, I’m happy to assist :)"
            return {"messages": [{"role": "assistant", "content": content}]}
        # hitl placeholder

    # ------------------------------------------------------------------
    # 4) Build normal assistant response
    # ------------------------------------------------------------------
    response_messages = [
        {"role": "assistant" if isinstance(m, AIMessage) else "user", "content": m.content}
        for m in agent_state.get("messages", [])
    ]

    return {"messages": response_messages}


@app.post("/api/agent/chat/stream", summary="Server-sent events streaming endpoint")
async def chat_stream(request: ChatRequest, req: Request):
    """Return the agent response as a stream (single final event for now)."""

    if not request.messages:
        raise HTTPException(status_code=400, detail="`messages` can not be empty")

    latest_user_msg = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
    if latest_user_msg is None:
        raise HTTPException(status_code=400, detail="At least one message with role == 'user' is required")

    # Build the async generator producing the SSE events
    async def event_generator():
        agent_result = await _invoke_agent(latest_user_msg.content if isinstance(latest_user_msg.content, str) else " ".join(
            p.text or "" for p in latest_user_msg.content  # type: ignore[attr-defined]
        ))

        # Serialize result
        response_payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "messages": [
                {
                    "role": "assistant" if isinstance(m, AIMessage) else "user",
                    "content": m.content,
                }
                for m in agent_result.get("messages", [])
            ],
        }

        yield {
            "event": "agent_response",
            "data": json.dumps(response_payload, ensure_ascii=False),
        }

    return EventSourceResponse(event_generator(), media_type="text/event-stream", sep="\n")

