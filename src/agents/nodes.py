import logging
from langchain_core.messages import HumanMessage
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
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "test_agent", result["messages"][-1].content
                    ),
                    name="test_agent",
                )
            ]
        },
        goto="__end__",
    )