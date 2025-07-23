from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class GuardrailBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Message ID")
    timestamp: Optional[datetime]  = Field(None, description="Timestamp")

class GuardrailCreate(GuardrailBase):
    toxicity: Dict[str, float] = Field(..., description="Toxic, obsceme, insult, sexual explicit")
    bias: Dict[str, float] = Field(..., description="Identity attack")
    privacy: Dict[str, bool] = Field(..., description="PII detected, secrets")
    prompt_attack: Dict[str, bool] = Field(..., description="Prompt injection, SQLi, template, XSS, ASCII, other")
    topic_relevance: bool = Field(..., description="Topic relevance")
    alignment: Dict[str, bool] = Field(..., description="Goal divergence")
    code_safety: Dict[str, bool] = Field(..., description="Code safety")
    formatting: Dict[str, bool] = Field(..., description="Valid JSON, SQL, CLI")
    model_explainability: Dict[str, bool] = Field(..., description="Confidence score")

class GuardrailUpdate(GuardrailBase):
    pass