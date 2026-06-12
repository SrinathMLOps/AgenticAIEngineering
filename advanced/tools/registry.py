"""
Advanced — Tool Registry with Result Caching
=============================================
What's new vs Intermediate:
  • Tool results are memoised per agent run.
  • If the agent calls the same tool with the same arguments twice, the second
    call is served instantly from the cache — no network round-trip.
  • file_io is excluded from caching because it has side effects (writes files).
  • Call clear_cache() between independent agent runs to reset state.

Why it matters:
  • Agents often re-ask the same question mid-loop (e.g. verify a search result).
  • Caching prevents redundant API calls, cuts latency, and reduces cost.
"""
import json
from tools import calculator, file_io, search, weather, wikipedia

REGISTRY: dict = {
    "web_search":       (search.TOOL_DEFINITION,    search.run),
    "calculator":       (calculator.TOOL_DEFINITION, calculator.run),
    "file_io":          (file_io.TOOL_DEFINITION,    file_io.run),
    "get_weather":      (weather.TOOL_DEFINITION,    weather.run),
    "wikipedia_search": (wikipedia.TOOL_DEFINITION,  wikipedia.run),
}

# Results are stored as: "{tool_name}:{sorted_json_input}" → result_string
_cache: dict[str, str] = {}

# These tools write to disk — never cache them
_NO_CACHE = {"file_io"}


def get_tool_definitions() -> list[dict]:
    """Return all tool definitions in the format the Anthropic API expects."""
    return [definition for definition, _ in REGISTRY.values()]


def clear_cache() -> None:
    """Reset the result cache (call this between independent agent runs)."""
    _cache.clear()


def dispatch(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """
    Run a tool by name.  Cacheable tools are served from memory on repeated calls.
    Returns (result_string, is_error).
    """
    if tool_name not in REGISTRY:
        return f"Unknown tool: {tool_name}. Available: {list(REGISTRY.keys())}", True

    cache_key = f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}"
    if tool_name not in _NO_CACHE and cache_key in _cache:
        return f"[cached] {_cache[cache_key]}", False

    _, run_fn = REGISTRY[tool_name]

    try:
        result = str(run_fn(**tool_input))
        if tool_name not in _NO_CACHE:
            _cache[cache_key] = result
        return result, False
    except TypeError as e:
        return f"Tool called with wrong arguments: {e}", True
    except Exception as e:
        return f"Tool execution failed: {type(e).__name__}: {e}", True
