import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent import HelpdeskAgent
from rag import RAGRetriever

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def print_banner():
    print("""
==================================================
              AI HELPDESK AGENT
==================================================

AI-powered technical troubleshooting assistant

Capabilities:
✓ AI Agent Reasoning
✓ RAG Knowledge Retrieval
✓ Real System Diagnostics
✓ Internet Diagnostics
✓ Disk Diagnostics
✓ CPU/RAM Diagnostics

Type 'help' for commands.
Type 'exit' to quit.
--------------------------------------------------""")

def print_help():
    print("""
Available Commands:
  help       - Show this help menu
  scenarios  - List example demonstration questions
  clear      - Clear the terminal screen
  exit / quit - Exit the application
""")

def print_scenarios():
    print("""
Suggested Demo Questions:
  1. "My laptop is connected to WiFi but I cannot access websites."
  2. "My laptop has become very slow."
  3. "My laptop is running out of storage."
  4. "My printer is connected but nothing is printing."
  5. "Chrome keeps crashing."
  6. "Who is the Prime Minister of India?" (Non-technical check)
""")

def main():
    # Initialize RAG Retriever & Agent
    print("\n[System] Initializing AI Helpdesk Agent engine...")
    retriever = RAGRetriever(data_dir="data", kb_dir="knowledge_base")
    agent = HelpdeskAgent(retriever=retriever)
    
    print_banner()

    while True:
        try:
            print("\nDescribe your technical problem:")
            user_input = input("> ").strip()

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            if cmd_lower in ["exit", "quit", "q"]:
                print("\nThank you for using AI Helpdesk Agent. Goodbye!\n")
                sys.exit(0)

            if cmd_lower == "help":
                print_help()
                continue

            if cmd_lower in ["scenarios", "examples", "demo"]:
                print_scenarios()
                continue

            if cmd_lower == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                continue

            # Process problem through Agent
            result = agent.process(user_input)

            # Print intermediate progress logs
            print("\n--------------------------------------------------")
            for log in result.get("logs", []):
                print(log)
            print("--------------------------------------------------\n")

            # Print Final Grounded Diagnosis Response
            print(result["response"])

        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting AI Helpdesk Agent. Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n[System Error] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
