import logging 
import re
import sys
from typing import Dict, List
from timeit import default_timer as timer
import pyprojroot
from guardrails.hub import ToxicLanguage
from guardrails import Guard

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from utils.helper import parse_regex
from config import config

logger = logging.getLogger(__name__)


def detect(message: str) -> Dict[str, bool]:

    toxicity_config = config["input_guardrails"]["toxicity"]

    guard = Guard().use(
    ToxicLanguage,
    threshold=toxicity_config["threshold"], 
    validation_method=toxicity_config["validation_method"], 
    on_fail=toxicity_config["on_fail"]
    )
    logger.info(f"toxicity guardrail initialized with labels : {toxicity_config['labels']} and action taken on failure : {toxicity_config['on_fail']}")

    toxicity_labels = toxicity_config["labels"]
    start_time = timer()
    result = guard.validate(str(message))
    print(result)
    end_time = timer()
    logger.info(f"Done, inference time: {end_time - start_time} seconds")
    if result.validation_passed:
        return {label: False for label in toxicity_labels}
    else:
        raw_label_text = result.validation_summaries[0].error_spans[0].reason
        
        detected_labels = parse_regex(raw_label_text,"Toxic language detected:")

        label_flags: Dict[str, bool] = {}
        for label in toxicity_labels:
            is_detected = any(
                dl == label.lower() for dl in detected_labels
            )
            label_flags[label] = is_detected

        return label_flags


if __name__ == "__main__":
    #print(detect("Love how you think and attack the problem. Great job!"))
    #print(detect("Please look carefully. You are a stupid idiot who can't do anything right."))
    print(detect("all jews are zionists"))
