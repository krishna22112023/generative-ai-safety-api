from sqlalchemy import Column, String, DateTime, Boolean, JSON
from app.db.base import Base

class Guardrail(Base):
    __tablename__ = "guardrails_result"

    user_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    toxicity = Column(JSON)
    bias = Column(JSON)
    privacy = Column(JSON)
    prompt_attack = Column(JSON)
    topic_relevance = Column(Boolean)
    alignment = Column(JSON)
    code_safety = Column(JSON)
    formatting = Column(JSON)
    model_explainability = Column(JSON)