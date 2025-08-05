"""Service layer for reading/writing chat related data and invoking the agent workflow."""
from __future__ import annotations

from typing import List, Dict, Any

from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from src.db.session import get_db  # noqa: F401  # import for typing only
from src.models.message import Message
from src.schema.chat import ChatRequest, ChatMessage
from src.schema.response import MessageCreate
from src.agents.workflow import run_agent_workflow


def _chatmessage_to_lc(msg: ChatMessage) -> BaseMessage:  # helper reused
    return HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content)


def process_chat(db: Session, payload: ChatRequest) -> Dict[str, Any]:
    """Run the agent and persist both user message and agent response.

    Returns the raw agent result for further use by the API layer.
    """

    # Convert messages to LangChain for the agent
    latest_user_msg = payload.messages[-1]
    lc_message = _chatmessage_to_lc(latest_user_msg)

    # Invoke agent synchronously (non-streaming)
    agent_state = run_agent_workflow(user_input=lc_message.content)

    # ------------------------------------------------------------------
    # Persist user message & agent response in a single row for now
    # (A real implementation could normalise this further.)
    # ------------------------------------------------------------------

    record = Message(
        user_id=payload.user_id,
        session_id=payload.session_id,
        message_id="msg_" + payload.session_id,
        response_id="resp_" + payload.session_id,
        message_content={
            "request": payload.model_dump(),
            "response": {
                "messages": [
                    {"role": "assistant" if isinstance(m, AIMessage) else "user", "content": m.content}
                    for m in agent_state.get("messages", [])
                ]
            },
        },
    )

    db.merge(record)  # merge => insert or update based on PK
    db.commit()

    return agent_state
