import logging 
import re
import sys
import os
from functools import lru_cache
from typing import Dict, List
from timeit import default_timer as timer
import pyprojroot
from guardrails.hub import GuardrailsPII
from guardrails import Guard

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from utils.helper import parse_regex, detect_secrets_regex
from config import config

logger = logging.getLogger(__name__)


def detect_pii(message: str) -> Dict[str, bool]:

    pii_config = config["input_guardrails"]["pii"]

    guard = Guard().use(
    GuardrailsPII,
    entities=pii_config["labels"],
    on_fail=pii_config["on_fail"]
    )
    logger.info(f"pii guardrail initialized with entities : {pii_config['labels']} and action taken on failure : {pii_config['on_fail']}")

    start_time = timer()
    result = guard.validate(str(message))
    end_time = timer()
    logger.info(f"Done, inference time: {end_time - start_time} seconds")

    pii_labels = pii_config["labels"]
    if result.validation_passed:
        return {label: 0 for label in pii_labels}
    else:
        label_flags: Dict[str, int] = {label: 0 for label in pii_labels}
        error_spans = result.validation_summaries[0].error_spans
        for label in pii_labels:
            for error_span in error_spans:
                if label == error_span.reason:
                    label_flags[label] += 1

        return label_flags

@lru_cache(maxsize=1)
def _load_yara_rules():
    """Compile and cache YARA rules used for secret detection."""
    try:
        import yara  # type: ignore
    except ImportError:
        return None

    rules_path = os.path.join(root, "config", "secrets_rules.yar")
    if not os.path.exists(rules_path):
        logger.warning("YARA rules file not found at %s. Falling back to regex detection.", rules_path)
        return None

    try:
        return yara.compile(filepath=rules_path)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to compile YARA rules: %s", exc)
        return None


def detect_secrets(message: str) -> Dict[str, int]:
    """Detect secret patterns in *message*.

    Tries YARA rules first; falls back to pure Python regex patterns if yara-python
    is unavailable or rule compilation fails.
    """

    secrets_config = config["input_guardrails"]["secrets"]
    labels: List[str] = secrets_config["labels"]

    start_time = timer()

    rules = _load_yara_rules()
    label_flags: Dict[str, int] = {label: 0 for label in labels}

    if rules is not None:
        try:
            matches = rules.match(data=message)
            for match in matches:
                # Each match.strings is a list of (offset, string_id, data)
                label = match.rule
                if label in label_flags:
                    label_flags[label] += len(match.strings) if match.strings else 1
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("YARA matching failed: %s. Falling back to regex.", exc)
            label_flags = detect_secrets_regex(message, labels)
    else:
        # YARA not available, fallback to regex
        label_flags = detect_secrets_regex(message, labels)

    end_time = timer()
    logger.info("Secret detection completed in %s seconds", end_time - start_time)

    return label_flags


if __name__ == "__main__":
    #print(detect_pii("my name is john doe, call me at 935523534, living at 123, main street, singapore and my fin number is G254523"))
    meta = """
        user_id = "1234"
        user_pwd = "password1234"
        user_api_key = "sk-xhdfgtest"
        """
    print(detect_secrets(meta))  
