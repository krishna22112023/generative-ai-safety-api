import logging
import sys
import pyprojroot
from langchain_community.tools.tavily_search import TavilySearchResults

root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from config import agent_config
from utils.agent import create_logged_tool

logger = logging.getLogger(__name__)

# Initialize Tavily search tool with logging
LoggedTavilySearch = create_logged_tool(TavilySearchResults)
tavily_tool = LoggedTavilySearch(name=agent_config["tools"]["tavily"]["name"], max_results=agent_config["tools"]["tavily"]["max_results"])