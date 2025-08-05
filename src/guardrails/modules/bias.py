from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import pyprojroot
import logging
from typing import Any, Dict, List
from timeit import default_timer as timer

from pydantic import BaseModel, Field, ValidationError
from groq import Groq

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from config import guardrail_config 
logger = logging.getLogger(__name__)

_BIAS_LABELS: List[str] = guardrail_config["input_guardrails"]["bias"]["labels"] 

_GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

class _BiasOutputModel(BaseModel):
    """Structured output model – every label maps to a boolean."""

    physical: bool = Field(False, description="Physical bias present")
    socioeconomic: bool = Field(False, description="Socio-economic bias present")
    gender: bool = Field(False, description="Gender bias present")
    racial: bool = Field(False, description="Racial bias present")
    age: bool = Field(False, description="Age bias present")

    @classmethod
    def from_llm_json(cls, raw: dict) -> "_BiasOutputModel":
        """Create instance from llm JSON containing a `bias_type` list."""
        flags = {label: False for label in _BIAS_LABELS}
        for label in raw.get("bias_type", []):
            if label in flags:
                flags[label] = True
        return cls(**flags)  # type: ignore[arg-type]


def detect_bias(text: str, *, model: str = "llama-3.1-8b-instant", temperature: float = 0.0) -> Dict[str, Any]:
    """Detect bias types in *text* using Groq LLM.

    Parameters
    ----------
    text : str
        Input string to analyse.
    model : str, optional
        Groq model identifier (default ``"llama-3.1-8b-instant"``).
    temperature : float, optional
        Sampling temperature passed to the model.

    Returns
    -------
    Dict[str, bool]
        Mapping of each bias label → bool. Labels are taken from
        ``config/config.json`` so they stay in sync with configuration.
    """
    prompt_path = Path(__file__).resolve().parent.parent / "prompts/bias.md"
    with prompt_path.open("r", encoding="utf-8") as fp:
        system_prompt = fp.read().strip()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    start_time = timer()
    completion = _GROQ_CLIENT.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    end_time = timer()
    raw_content = completion.choices[0].message.content.strip()
    logger.info(f"bias detection time: {end_time - start_time} seconds")
    logger.info(f"bias detection result: {raw_content}")
    
    parsed_json: dict
    try:
        parsed_json = json.loads(raw_content)
    except json.JSONDecodeError:
        try:
            start = raw_content.find("{")
            end = raw_content.rfind("}") + 1
            parsed_json = json.loads(raw_content[start:end])
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                "Groq response could not be parsed as JSON:", raw_content
            ) from exc
    try:
        bias_output_model = _BiasOutputModel.from_llm_json(parsed_json)
    except ValidationError as exc:  # pragma: no cover
        raise RuntimeError("Unexpected fields in LLM response") from exc

    # Build standardized response
    return {
        "result": bias_output_model.model_dump(),
        "reason": {"explanation": parsed_json.get("reason", "")},
        "run_time": end_time - start_time,
    }

if __name__ == "__main__":
    text = "i think i lean right on the political spectrum"
    print(detect_bias(text))