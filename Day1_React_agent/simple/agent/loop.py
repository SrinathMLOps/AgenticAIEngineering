"""
Simple — ReAct Agent Loop
==========================
What you learn here:
  1. How to call the Anthropic API with tools
  2. How to read the stop_reason to know if the model wants to call a tool
  3. How to send tool results back and keep the loop going
  4. How to stop cleanly when the model says it's done

New tools added at this level (vs the original project):
  • get_weather   — free Open-Meteo API, no key needed
  • wikipedia_search — lookup any topic via the Wikipedia API

MAX_STEPS is raised to 15 so the agent has room for longer research tasks.
"""
import os
import anthropic
from memory.buffer import ConversationBuffer
from tools.registry import dispatch, get_tool_definitions
from utils.logger import log_act, log_finish, log_observe, log_step, log_think
from utils.schema import ToolCall

MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))  # raised from 10 so longer tasks can finish

SYSTEM_PROMPT = """You are a capable AI agent that solves tasks step by step.

You have access to tools: web_search, calculator, file_io, get_weather, wikipedia_search.

## How to behave
- Think carefully before acting. Use tools only when needed.
- After each tool result, reflect on what you learned before deciding the next step.
- When you have enough information, respond with your final answer directly (no tool call).
- Be concise in your reasoning. Prioritise accuracy over speed.
- If a tool fails, try a different approach — don't give up immediately.

## Important
- Never make up facts. If you don't know something, search or look it up.
- Always verify calculations with the calculator tool.
- Save important results to a file if the user might want to keep them.
"""


def run_agent(task: str) -> str:
    """Run the ReAct loop for a given task. Returns the final answer as a string."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    memory = ConversationBuffer()
    memory.add_user(task)

    tools = get_tool_definitions()

    for step in range(1, MAX_STEPS + 1):
        log_step(step, MAX_STEPS)

        # ── THINK ──────────────────────────────────────────────────────────
        # Ask the model what to do next. It either picks a tool or gives a
        # final answer (stop_reason == "end_turn").
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=memory.get_messages(),
        )

        # Keep the assistant turn in memory so the model has context
        memory.add_assistant(response.content)

        # ── FINISHED ───────────────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            final_text = _extract_text(response.content)
            log_think(final_text)
            log_finish(final_text)
            return final_text

        # ── ACT + OBSERVE ──────────────────────────────────────────────────
        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "text" and block.text:
                    log_think(block.text)

                if block.type == "tool_use":
                    tool_call = ToolCall(id=block.id, name=block.name, input=block.input)
                    log_act(tool_call.name, tool_call.input)

                    # Run the tool and feed the result back to the model
                    result, is_error = dispatch(tool_call.name, tool_call.input)
                    log_observe(result, is_error)

                    memory.add_tool_result(tool_call.id, result, is_error)
            continue

        break  # unexpected stop_reason

    return "Agent reached the maximum number of steps without completing the task."


def _extract_text(content: list) -> str:
    parts = [block.text for block in content if hasattr(block, "text") and block.text]
    return "\n".join(parts) if parts else "No text response."
