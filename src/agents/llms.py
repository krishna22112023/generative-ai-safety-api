from langchain_openai import ChatOpenAI
from typing import Optional

def create_openai_llm(
    model: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    **kwargs,
) -> ChatOpenAI:
    """
    Create a ChatOpenAI instance with the specified configuration
    """
    # Only include base_url in the arguments if it's not None or empty
    llm_kwargs = {"model": model, "temperature": temperature, **kwargs}

    if base_url:  # This will handle None or empty string
        llm_kwargs["base_url"] = base_url

    if api_key:  # This will handle None or empty string
        llm_kwargs["api_key"] = api_key

    return ChatOpenAI(**llm_kwargs)


