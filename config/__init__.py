import json
import pyprojroot
from pathlib import Path
from dotenv import load_dotenv

guardrail_config = json.load(open("config/guardrail_config.json"))
agent_config = json.load(open("config/agent_config.json"))

root = pyprojroot.find_root(pyprojroot.has_dir("config"))
load_dotenv(Path(root, ".env"))






