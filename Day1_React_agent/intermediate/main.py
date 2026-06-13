"""
Intermediate ReAct Agent
=========================
Run:  python main.py
      python main.py "Explain quantum entanglement in simple terms"

What's new vs Simple:
  • Streaming output  — tokens appear in real time (set STREAM_OUTPUT=false to disable)
  • Retry on error    — tool failures are automatically retried (MAX_RETRIES=2)
  • Token tracker     — cost per run is displayed after every task
"""
from dotenv import load_dotenv

load_dotenv()

from agent.runner import run_interactive, run_single
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_single(" ".join(sys.argv[1:]))
    else:
        run_interactive()
