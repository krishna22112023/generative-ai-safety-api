from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Chat message used by front-end.

    The internal agent uses LangChain ``BaseMessage`` objects whereas the
    public API uses this simplified schema (role/content).  Conversion
    helpers are provided below.
    """

    role: str = Field(..., description="The role of the sender (user/assistant)")
    content: str = Field(..., description="The content of the message")

class ChatRequest(BaseModel):
    """Request body for the /api/agent/chat* endpoints."""

    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    messages: List[ChatMessage] = Field(..., description="Conversation history")
    search: Optional[bool] = Field(False, description="Whether to enable search tools")
    code: Optional[bool] = Field(False, description="Whether to enable code tools")
