import os
import sys
import pyprojroot
from langgraph.prebuilt import create_react_agent

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from utils.agent import apply_prompt_template
from src.agents.tools import (
    tavily_tool
)
from config import agent_config
from .llms import create_openai_llm

OPEN_API_KEY = os.getenv("OPEN_API_KEY")

llm = create_openai_llm(
            model=agent_config["llm"]["model"],
            api_key=OPEN_API_KEY,
        )

test_agent = create_react_agent(
    llm,
    tools=[tavily_tool],
    prompt=lambda state: apply_prompt_template("test_agent", state),
)
