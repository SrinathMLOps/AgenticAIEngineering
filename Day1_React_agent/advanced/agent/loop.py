"""
Advanced — ReAct Agent Loop
=============================
Builds on everything in Intermediate and adds two more features:

1. PLAN-FIRST STEP (PLAN_FIRST=true, default on)
   ─────────────────────────────────────────────
   Before the ReAct loop starts, the agent is asked to produce a numbered
   plan (3–5 steps). The plan is shown in a magenta panel and then prepended
   to the task so the model follows its own roadmap during execution.

   Why it matters: for complex multi-step tasks, planning first reduces
   mid-loop course corrections and makes the agent's reasoning more
   predictable and auditable.

2. TOOL RESULT CACHING  (lives in tools/registry.py)
   ────────────────────────────────────────────────
   Results from cacheable tools are stored in a dict keyed by
   "{tool_name}:{sorted_json_input}". If the agent calls the same tool with
   the same arguments again, the cached answer is returned instantly — no
   network call, no tokens wasted on re-fetching identical data.

   file_io is excluded from the cache because writing to disk is a
   side effect that must always execute.

Inherited from Intermediate:
  • Streaming output
  • Retry on tool error
  • Token usage tracker
"""
import os
import anthropic
from memory.buffer import ConversationBuffer
from tools.registry import dispatch, get_tool_definitions
from utils.logger import log_act, log_finish, log_observe, log_plan, log_step, log_think, log_token_usage
from utils.schema import ToolCall

MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
STREAM_OUTPUT = os.getenv("STREAM_OUTPUT", "true").lower() == "true"
PLAN_FIRST = os.getenv("PLAN_FIRST", "true").lower() == "true"   # NEW

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

_PLAN_PROMPT = """\
Before taking any action, output a numbered plan (3–5 steps) describing exactly \
how you will approach this task. Format:

Plan:
1. …
2. …
…

End with a line containing only: READY

Do not call any tools yet — just plan."""


# ── NEW: plan-first phase ─────────────────────────────────────────────────────

def _plan_phase(client: anthropic.Anthropic, task: str) -> str:
    """
    Ask the model for a plan before the main loop starts.
    A separate, tool-free API call forces the model to think structurally.
    The plan text is logged and then injected into the task so the main loop
    has a clear roadmap to follow.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": f"Task: {task}\n\n{_PLAN_PROMPT}"}],
    )
    plan_text = _extract_text(response.content)
    log_plan(plan_text)
    return plan_text


# ── Streaming API helper ──────────────────────────────────────────────────────

def _call_api(
    client: anthropic.Anthropic,
    memory: ConversationBuffer,
    tools: list,
) -> anthropic.types.Message:
    kwargs = dict(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=memory.get_messages(),
    )
    if STREAM_OUTPUT:
        with client.messages.stream(**kwargs) as stream:
            print("\033[34m", end="", flush=True)
            for token in stream.text_stream:
                print(token, end="", flush=True)
            print("\033[0m", flush=True)
            return stream.get_final_message()
    return client.messages.create(**kwargs)


# ── Retry dispatcher ──────────────────────────────────────────────────────────

def _dispatch_with_retry(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    result, is_error = dispatch(tool_name, tool_input)
    if not is_error:
        return result, False
    for attempt in range(1, MAX_RETRIES + 1):
        log_observe(f"Retry {attempt}/{MAX_RETRIES} for '{tool_name}'…", is_error=False)
        result, is_error = dispatch(tool_name, tool_input)
        if not is_error:
            return result, False
    return result, is_error


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_agent(task: str) -> str:
    """Run the ReAct loop for a given task. Returns the final answer as a string."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    memory = ConversationBuffer()
    tools = get_tool_definitions()

    total_input_tokens = 0
    total_output_tokens = 0

    # NEW: plan-first — generate and inject the plan before the loop
    if PLAN_FIRST:
        plan = _plan_phase(client, task)
        task = f"{task}\n\n[Your plan]\n{plan}\n\nNow execute your plan step by step."

    memory.add_user(task)

    for step in range(1, MAX_STEPS + 1):
        log_step(step, MAX_STEPS)

        response = _call_api(client, memory, tools)

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        memory.add_assistant(response.content)

        if response.stop_reason == "end_turn":
            final_text = _extract_text(response.content)
            if not STREAM_OUTPUT:
                log_think(final_text)
            log_finish(final_text)
            log_token_usage(total_input_tokens, total_output_tokens)
            return final_text

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "text" and block.text and not STREAM_OUTPUT:
                    log_think(block.text)
                if block.type == "tool_use":
                    tool_call = ToolCall(id=block.id, name=block.name, input=block.input)
                    log_act(tool_call.name, tool_call.input)
                    result, is_error = _dispatch_with_retry(tool_call.name, tool_call.input)
                    log_observe(result, is_error)
                    memory.add_tool_result(tool_call.id, result, is_error)
            continue

        break

    log_token_usage(total_input_tokens, total_output_tokens)
    return "Agent reached the maximum number of steps without completing the task."


def _extract_text(content: list) -> str:
    parts = [block.text for block in content if hasattr(block, "text") and block.text]
    return "\n".join(parts) if parts else "No text response."
