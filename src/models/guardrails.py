from sqlalchemy import Column, String, DateTime, Boolean, JSON
from src.db.base import Base

class Guardrail(Base):
    __tablename__ = "guardrails_response"

    user_id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    session_id = Column(String, index=True,nullable=False)
    message_id = Column(String, nullable=True)
    toxicity = Column(JSON)
    bias = Column(JSON)
    ethics = Column(JSON)
    pii = Column(JSON)
    secrets = Column(JSON)
    prompt_safety = Column(JSON)
    tool_alignment = Column(JSON)
    code_shield = Column(JSON)