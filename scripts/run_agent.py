"""
Entry point script for the LangGraph Demo.
"""

import sys
import logging
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("src"))
sys.path.append(str(root))
from src.agents.workflow import run_agent_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    import sys
    while True: 
        if len(sys.argv) > 1:
            user_query = " ".join(sys.argv[1:])
        else:
            user_query = input("Enter your query: ")
        
        if user_query == "exit" or user_query == "quit":
            break

        result = run_agent_workflow(user_input=user_query)

        # Print the conversation history
        print("\n=== Conversation History ===")
        for message in result["messages"]:
            role = message.type
            print(f"\n[{role.upper()}]: {message.content}")