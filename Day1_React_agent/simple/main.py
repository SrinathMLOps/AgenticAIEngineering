"""
Simple ReAct Agent
==================
Run:  python main.py
      python main.py "What is the weather in Paris today?"

New at this level vs the base project:
  • get_weather      — current conditions + forecast for any city (Open-Meteo, free)
  • wikipedia_search — instant Wikipedia lookup for any topic
  • MAX_STEPS = 15   — enough room for multi-step research tasks
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
