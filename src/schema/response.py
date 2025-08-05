from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str = Field(..., description="Unique identifier for the message")
    session_id: str = Field(..., description="ID of the conversation this message belongs to")
    message_id: Optional[str] = Field(None, description="Unique ID of the message")
    response_id: Optional[str] = Field(None, description="ID of the response related to this message")
    message_content: Dict[str, Any] = Field(..., description="Content of the message in JSON format")


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    pass


class MessageResponse(MessageBase):
    pass