from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def import_models():
    # Import llm here within the function to avoid circular imports
    from src.models.guardrails import Guardrail