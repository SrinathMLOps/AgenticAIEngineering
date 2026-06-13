"""
Advanced ReAct Agent
=====================
Run:  python main.py
      python main.py "Research the history of AI and save a report"

What's new vs Intermediate:
  • Plan-first       — agent outputs a numbered plan before acting (PLAN_FIRST=true)
  • Tool caching     — identical tool calls are served from memory (see tools/registry.py)

Inherited from Intermediate:
  • Streaming output  (STREAM_OUTPUT=true)
  • Retry on error    (MAX_RETRIES=2)
  • Token tracker     — cost shown after every run

Bonus:
  • eval_harness.py  — run 5 benchmark tasks and measure pass/fail accuracy
                       python eval_harness.py
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
