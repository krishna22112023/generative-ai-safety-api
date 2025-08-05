import logging 
import re
import sys
import os
from typing import Any, Dict, List
from timeit import default_timer as timer
import pyprojroot
from guardrails.hub import GuardrailsPII
from guardrails import Guard

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from utils.helper import parse_regex, detect_secrets_regex
from config import guardrail_config

logger = logging.getLogger(__name__)


def detect_pii(message: str) -> Dict[str, Any]:

    pii_config = guardrail_config["input_guardrails"]["pii"]

    guard = Guard().use(
    GuardrailsPII,
    entities=pii_config["labels"]
    )
    logger.info(f"pii guardrail initialized with entities : {pii_config['labels']}")

    start_time = timer()
    result = guard.validate(str(message))
    end_time = timer()
    logger.info("Done, inference time: %s seconds", end_time - start_time)

    pii_labels = pii_config["labels"]
    label_flags: Dict[str, int] = {label: 0 for label in pii_labels}

    if not result.validation_passed:
        error_spans = result.validation_summaries[0].error_spans
        for error_span in error_spans:
            reason_label = getattr(error_span, "reason", "")
            if reason_label in label_flags:
                label_flags[reason_label] += 1

    return {
        "result": label_flags,
        "reason": {},
        "run_time": end_time - start_time,
    }


def detect_secrets(message: str) -> Dict[str, Any]:
    """Detect secret patterns using comprehensive regular expressions."""

    secrets_config = guardrail_config["input_guardrails"]["secrets"]
    labels: List[str] = secrets_config["labels"]

    start_time = timer()
    
    # Use enhanced regex detection from helper.py
    label_flags = detect_secrets_regex(message, labels)

    end_time = timer()
    logger.info("Secret detection completed in %s seconds", end_time - start_time)

    return {
        "result": label_flags,
        "reason": {},
        "run_time": end_time - start_time,
    }


if __name__ == "__main__":
    #print(detect_pii("my name is john doe, call me at 935523534, living at 123, main street, singapore and my fin number is G254523"))
    meta = """
    'USER_ID = admin123',
    'password = mySecretPass123!',
    'API_KEY = sk-abcd1234567890abcdef',
    'encryption_key = MIIEpAIBAAKCAQEA1234567890abcdef'
    """
    print(detect_secrets(meta))  
