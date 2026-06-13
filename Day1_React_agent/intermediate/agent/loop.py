"""
Intermediate — ReAct Agent Loop
=================================
What's new vs Simple:

1. STREAMING OUTPUT (STREAM_OUTPUT=true, default on)
   ─────────────────────────────────────────────────
   Instead of waiting for the full response, tokens print to the terminal
   as they are generated. This uses client.messages.stream() — a context
   manager that yields text deltas and then returns the final Message.

   Why it matters: for long reasoning steps the user sees progress in real
   time rather than a blank screen followed by a wall of text.

2. RETRY ON TOOL ERROR (MAX_RETRIES=2, default)
   ────────────────────────────────────────────
   If a tool returns is_error=True (network timeout, bad input, etc.) the
   dispatcher retries the same call up to MAX_RETRIES more times before
   giving up. Transient failures (DNS hiccups, rate limits) are silently
   recovered.

3. TOKEN USAGE TRACKER
   ─────────────────────
   Every API response contains a usage object with input_tokens and
   output_tokens. We accumulate them across all steps and print the total
   cost at the end of each run using logger.log_token_usage().
"""
import os
import anthropic
from memory.buffer import ConversationBuffer
from tools.registry import dispatch, get_tool_definitions
from utils.logger import log_act, log_finish, log_observe, log_step, log_think, log_token_usage
from utils.schema import ToolCall

MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))          # how many extra attempts on tool error
STREAM_OUTPUT = os.getenv("STREAM_OUTPUT", "true").lower() == "true"

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


# ── NEW: streaming helper ──────────────────────────────────────────────────────

def _call_api(
    client: anthropic.Anthropic,
    memory: ConversationBuffer,
    tools: list,
) -> anthropic.types.Message:
    """
    Make one model call.

    When STREAM_OUTPUT is True, text tokens are printed live as they arrive.
    We use client.messages.stream() which is a context manager; calling
    .get_final_message() at the end gives us the same Message object we would
    have gotten from client.messages.create(), so the rest of the loop is
    identical regardless of whether streaming is on or off.
    """
    kwargs = dict(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=memory.get_messages(),
    )
    if STREAM_OUTPUT:
        with client.messages.stream(**kwargs) as stream:
            print("\033[34m", end="", flush=True)   # blue tint while streaming
            for token in stream.text_stream:
                print(token, end="", flush=True)
            print("\033[0m", flush=True)
            return stream.get_final_message()

    return client.messages.create(**kwargs)


# ── NEW: retry dispatcher ─────────────────────────────────────────────────────

def _dispatch_with_retry(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """
    Call a tool.  On error, retry up to MAX_RETRIES more times.
    Retrying the same call handles transient failures (timeouts, rate limits).
    """
    result, is_error = dispatch(tool_name, tool_input)
    if not is_error:
        return result, False

    for attempt in range(1, MAX_RETRIES + 1):
        log_observe(f"Retry {attempt}/{MAX_RETRIES} for '{tool_name}'…", is_error=False)
        result, is_error = dispatch(tool_name, tool_input)
        if not is_error:
            return result, False

    return result, is_error  # all retries exhausted


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_agent(task: str) -> str:
    """Run the ReAct loop for a given task. Returns the final answer as a string."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    memory = ConversationBuffer()
    memory.add_user(task)

    tools = get_tool_definitions()

    # NEW: accumulate token counts across every API call in this run
    total_input_tokens = 0
    total_output_tokens = 0

    for step in range(1, MAX_STEPS + 1):
        log_step(step, MAX_STEPS)

        response = _call_api(client, memory, tools)

        # NEW: add this response's tokens to the running totals
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        memory.add_assistant(response.content)

        if response.stop_reason == "end_turn":
            final_text = _extract_text(response.content)
            if not STREAM_OUTPUT:
                log_think(final_text)
            log_finish(final_text)
            log_token_usage(total_input_tokens, total_output_tokens)  # NEW
            return final_text

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "text" and block.text and not STREAM_OUTPUT:
                    log_think(block.text)

                if block.type == "tool_use":
                    tool_call = ToolCall(id=block.id, name=block.name, input=block.input)
                    log_act(tool_call.name, tool_call.input)

                    result, is_error = _dispatch_with_retry(tool_call.name, tool_call.input)  # NEW
                    log_observe(result, is_error)

                    memory.add_tool_result(tool_call.id, result, is_error)
            continue

        break

    log_token_usage(total_input_tokens, total_output_tokens)
    return "Agent reached the maximum number of steps without completing the task."


def _extract_text(content: list) -> str:
    parts = [block.text for block in content if hasattr(block, "text") and block.text]
    return "\n".join(parts) if parts else "No text response."
