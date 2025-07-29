import logging
import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from src.agents.builder import build_graph

logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()


def run_agent_workflow(user_input: str):
    """Run the agent workflow with the given user input.

    Args:
        user_input: The user's query or request
        debug: If True, enables debug level logging

    Returns:
        The final state after the workflow completes
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    logger.info(f"Starting workflow with user input: {user_input}")
    result = graph.invoke(
        {
            "messages": [{"role": "user", "content": user_input}],
        }
    )
    logger.debug(f"Final workflow state: {result}")
    logger.info("Workflow completed successfully")
    return result