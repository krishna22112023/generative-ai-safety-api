from sqlalchemy import Column, String, JSON
from src.db.base import Base

class Message(Base):
    __tablename__ = 'agent_response'

    user_id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    message_id = Column(String, nullable=True)
    response_id = Column(String, nullable=True)
    message_content = Column(JSON, nullable=False)
