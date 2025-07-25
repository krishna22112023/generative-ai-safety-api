import json
import pyprojroot
from pathlib import Path
from dotenv import load_dotenv

config = json.load(open("config/config.json"))

root = pyprojroot.find_root(pyprojroot.has_dir("config"))
load_dotenv(Path(root, ".env"))






