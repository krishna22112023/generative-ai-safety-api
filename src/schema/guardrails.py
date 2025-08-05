from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class GuardrailBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Message ID")
    toxicity: Dict[str, float] = Field(..., description="Toxic, obsceme, insult, sexual explicit")
    bias: Dict[str, float] = Field(..., description="Identity attack")
    ethics: Dict[str, bool] = Field(..., description="Ethics")
    pii: Dict[str, bool] = Field(..., description="PII detected, secrets")
    secrets: Dict[str, bool] = Field(..., description="Secrets detected")
    prompt_safety: Dict[str, bool] = Field(..., description="Prompt injection, SQLi, template, XSS, ASCII, other")
    tool_alignment: Dict[str, bool] = Field(..., description="Goal divergence")
    code_shield: Dict[str, bool] = Field(..., description="Code safety")

class GuardrailCreate(GuardrailBase):
    pass

class GuardrailUpdate(GuardrailBase):
    pass

class GuardrailResponse(GuardrailBase):
    pass