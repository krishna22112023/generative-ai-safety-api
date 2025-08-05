import logging
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from src.agents.agents import test_agent
from src.agents.types import State

logger = logging.getLogger(__name__)

RESPONSE_FORMAT = "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"


def agent_node(state: State):
    logger.info("agent starting task")
    result = test_agent.invoke(state)
    logger.info("agent completed task")
    logger.debug(f"agent response: {result['messages'][-1].content}")

    # Identify new ToolMessage instances produced during this invocation
    previous_messages = state.get("messages", [])
    new_messages = [msg for msg in result["messages"] if msg not in previous_messages]
    tool_messages = [msg for msg in new_messages if isinstance(msg, ToolMessage)]

    # Form the assistant's final response
    ai_response = AIMessage(
        content=RESPONSE_FORMAT.format(
            "test_agent", result["messages"][-1].content
        ),
        name="test_agent",
    )

    return Command(
        update={
            "messages": tool_messages + [ai_response]
        },
        goto="__end__",
    )