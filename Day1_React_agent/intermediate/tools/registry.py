"""
Simple — Tool Registry
=======================
Identical to the Simple registry.
No caching yet — that is added in the Advanced level.
"""
from tools import calculator, file_io, search, weather, wikipedia

REGISTRY: dict = {
    "web_search":       (search.TOOL_DEFINITION,    search.run),
    "calculator":       (calculator.TOOL_DEFINITION, calculator.run),
    "file_io":          (file_io.TOOL_DEFINITION,    file_io.run),
    "get_weather":      (weather.TOOL_DEFINITION,    weather.run),
    "wikipedia_search": (wikipedia.TOOL_DEFINITION,  wikipedia.run),
}


def get_tool_definitions() -> list[dict]:
    """Return all tool definitions in the format the Anthropic API expects."""
    return [definition for definition, _ in REGISTRY.values()]


def dispatch(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """
    Run a tool by name with given inputs.
    Returns (result_string, is_error).
    """
    if tool_name not in REGISTRY:
        return f"Unknown tool: {tool_name}. Available: {list(REGISTRY.keys())}", True

    _, run_fn = REGISTRY[tool_name]

    try:
        result = run_fn(**tool_input)
        return str(result), False
    except TypeError as e:
        return f"Tool called with wrong arguments: {e}", True
    except Exception as e:
        return f"Tool execution failed: {type(e).__name__}: {e}", True
