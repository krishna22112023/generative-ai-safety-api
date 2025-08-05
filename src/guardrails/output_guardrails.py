"""Refer to the output guardrails for the output messages :
1. tool alignment : detect if CoT of agent and tool called is aligned to user objective
2. code shield : detect if the tool is using code that is not allowed
Please first call the utils.tool_alignment.workflow_result_to_trace() to convert the result to a trace, then call the alignment and code shield functions
"""

import sys
import logging
import pyprojroot
from llamafirewall import Trace

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from src.guardrails.modules import tool_alignment
from config import guardrail_config
logger = logging.getLogger(__name__)

def output_guardrails(message: Trace) -> dict:
    """
    Run all input guardrails on the input message
    """
    output_guardrails_config = guardrail_config.get("output_guardrails", {})
    results = {key: {} for key in output_guardrails_config.keys()}

    if "tool_alignment" in output_guardrails_config:
        results["tool_alignment"] = tool_alignment.run_alignment_check(message)
    if "code_shield" in output_guardrails_config:
        # Pass only the assistant's latest message to CodeShield
        from llamafirewall import AssistantMessage
        last_assistant = next((m for m in reversed(message) if isinstance(m, AssistantMessage)), None)
        if last_assistant is not None:
            results["code_shield"] = tool_alignment.run_code_shield_check(last_assistant)
        else:
            results["code_shield"] = None

    return results

if __name__ == "__main__":
    #call agent/llm workflow. for this example, we use a langgraph agent workflow
    from src.agents.workflow import run_agent_workflow
    from src.guardrails.modules.tool_alignment import run_alignment_check, display_scan_result
    from utils.tool_alignment import workflow_result_to_trace
    while True: 
        if len(sys.argv) > 1:
            user_query = " ".join(sys.argv[1:])
        else:
            user_query = input("Enter your query: ")
        
        if user_query == "exit" or user_query == "quit":
            break

        result = run_agent_workflow(user_input=user_query)
        logger.info(f"Result: {result}")
        trace = workflow_result_to_trace(result)
        output_guardrails_result = output_guardrails(trace)
        display_scan_result(output_guardrails_result["tool_alignment"], "Tool Alignment")
        display_scan_result(output_guardrails_result["code_shield"], "Code Shield")

        # Print the conversation history
        print("\n=== Conversation History ===")
        for message in result["messages"]:
            role = message.type
            print(f"\n[{role.upper()}]: {message.content}")