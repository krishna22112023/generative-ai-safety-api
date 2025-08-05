import logging 
import re
import sys
from typing import Any, Dict, List
from timeit import default_timer as timer
import pyprojroot
from guardrails.hub import ToxicLanguage
from guardrails import Guard

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from utils.helper import parse_regex
from config import guardrail_config

logger = logging.getLogger(__name__)


def detect_toxicity(message: str) -> Dict[str, Any]:

    toxicity_config = guardrail_config["input_guardrails"]["toxicity"]

    guard = Guard().use(
    ToxicLanguage,
    threshold=toxicity_config["threshold"], 
    validation_method=toxicity_config["validation_method"]
    )
    logger.info(f"toxicity guardrail initialized with labels : {toxicity_config['labels']}")

    toxicity_labels = toxicity_config["labels"]
    start_time = timer()
    result = guard.validate(str(message))
    end_time = timer()
    logger.info("Done, inference time: %s seconds", end_time - start_time)

    if result.validation_passed:
        label_flags_bool: Dict[str, bool] = {label: False for label in toxicity_labels}
    else:
        raw_label_text = result.validation_summaries[0].error_spans[0].reason
        detected_labels = parse_regex(raw_label_text, "Toxic language detected:")

        label_flags_bool: Dict[str, bool] = {}
        for label in toxicity_labels:
            is_detected = any(dl == label.lower() for dl in detected_labels)
            label_flags_bool[label] = is_detected

    return {
        "result": label_flags_bool,
        "reason": {},
        "run_time": end_time - start_time,
    }


if __name__ == "__main__":
    #print(detect("Love how you think and attack the problem. Great job!"))
    #print(detect("Please look carefully. You are a stupid idiot who can't do anything right."))
    print(detect_toxicity("all jews are zionists"))
