"""
Tool alignment checks for agentic LLMs : 
1. Llamafirewall codeshield : 
Uses combination of regex and semgrep rules to detect detect code injections in the LLM's response.
source : https://github.com/meta-llama/PurpleLlama/blob/main/CodeShield/insecure_code_detector/rules/README.md

2. Llamafirewall AlignmentCheck 
A chain-of-thought auditing module that inspects the reasoning process of an LLM agent in real time. 
It uses few-shot prompting and semantic analysis to detect goal hijacking, indirect prompt injections, and signs of agent misalignment.

    Use case: Verifying that agent decisions remain consistent with user intent.
    Strengths: Deep introspection, detects subtle misalignment, works with opaque or black-box models.
source : https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall
"""

import json
import logging
import os
import sys
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, TypeVar, Union

from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig

Input = TypeVar("Input")
Output = TypeVar("Output")
Other = TypeVar("Other")

from llamafirewall import (
    AssistantMessage,
    LlamaFirewall,
    Role,
    ScannerType,
    ScanResult,
    Trace,
    UserMessage,
    ScanDecision,
)

logger = logging.getLogger(__name__)

class LlamaFirewallRunnableClass(Runnable[Input, Output]):
    """
    A Runnable compatible with langgraph agent that uses LlamaFirewall to scan the input and return the input if it is not blocked.
    """
    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Input,
    ) -> Input:
        """
        Process the input using the GR guardrail.
        """
        logger.debug(f"Input to process: {getattr(input, 'content', '')[:300]}")
        llamafirewall = LlamaFirewall()
        lf_input = AssistantMessage(
            content=getattr(input, "content", ""),
        )
        result = llamafirewall.scan(lf_input)
        if result.decision == ScanDecision.BLOCK:
            input.content = [f"Blocked by LlamaFirewall, {result.reason}"]

        logger.debug(f"Decision result: {result.decision}.")
        return input

    def __or__(
        self,
        other: Union[
            Runnable[Input, Other],
            Callable[[Input], Other],
            Callable[[Iterator[Input]], Iterator[Other]],
            Mapping[
                str, Union[Runnable[Input, Other], Callable[[Input], Other], Input]
            ],
        ],
    ) -> Runnable[Input, Output]:
        """
        Allow chaining with another runnable (or a LangChain chain) using the | operator.
        The output of this runnable will be passed as input to the next.
        """
        if (
            isinstance(other, Runnable)
            and hasattr(other, "invoke")
            and callable(other.invoke)
        ):
            # Define a composite runnable that calls self.invoke first, then passes the result to other.invoke.
            parent = self

            class CompositeRunnable(Runnable[Input, Output]):
                def invoke(
                    self,
                    input: Input,
                    config: Optional[RunnableConfig] = None,
                    **kwargs: Input,
                ) -> Output:
                    intermediate = parent.invoke(input, config=config, **kwargs)
                    return other.invoke(intermediate, config=config, **kwargs)

            return CompositeRunnable()
        else:
            raise ValueError(
                f"[LlamaFirewall] Langchain agent cannot chain with object of type: {type(other)}"
            )

def run_alignment_check(trace: Trace) -> Optional[ScanResult]:
    """
    Run AlignmentCheck scanner on the provided trace.

    Args:
        trace: The conversation trace to analyze. Refer to the get_sample_traces() to understand the format of the trace.

    Returns:
        Optional[ScanResult]: The scan result or None if an error occurred.
    """
    try:
        # Initialize LlamaFirewall with AlignmentCheck scanner
        scanner_config = {
            Role.ASSISTANT: [ScannerType.AGENT_ALIGNMENT],
        }
        firewall = LlamaFirewall(scanner_config)
        return firewall.scan_replay(trace)
    except Exception as e:
        logger.error(f"Error running alignment check: {str(e)}")
        return None

def run_code_shield_check(message: AssistantMessage) -> Optional[ScanResult]:
    """
    Run CodeShield scanner on the provided message

    Args:
        trace: The message to analyze.

    Returns:
        Optional[ScanResult]: The scan result or None if an error occurred.
    """
    try:
        # Initialize LlamaFirewall with CodeShield scanner
        scanner_config = {
            Role.ASSISTANT: [ScannerType.CODE_SHIELD],
        }
        firewall = LlamaFirewall(scanner_config)
        return firewall.scan(message)
    except Exception as e:
        logger.error(f"Error running code shield: {str(e)}")
        return None


def display_scan_result(result: Optional[ScanResult], description: str) -> None:
    """
    Display the scan result in a formatted way.

    Args:
        result: The scan result to display.
        description: Description of the scenario being tested.
    """
    print(f"\n\n=== Testing {description} ===")

    if result is None:
        logger.error("Scan failed to produce a result.")
        return

    print(
        f"=== Scan Result ===\n"
        f"Score: {result.score:.4f}\n"
        f"Decision: {result.decision}\n"
        f"Reason: {result.reason}\n"
        f"=================="
    )

def check_environment() -> bool:
    """
    Check if the required environment variables are set.

    Returns:
        bool: True if all required environment variables are set, False otherwise.
    """
    if not os.environ.get("TOGETHER_API_KEY"):
        logger.error(
            f"TOGETHER_API_KEY environment variable is not set. Please set it before running."
        )
        logger.info("You can get an API key from https://together.ai")
        return False
    return True



