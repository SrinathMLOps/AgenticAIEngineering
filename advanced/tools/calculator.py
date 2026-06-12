import ast
import math
import operator

TOOL_DEFINITION = {
    "name": "calculator",
    "description": (
        "Evaluate a mathematical expression safely. Supports arithmetic, "
        "powers, square roots, logarithms, trig functions, and Python math module. "
        "Examples: '2 ** 10', 'math.sqrt(144)', 'math.log(100, 10)'."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A valid Python math expression to evaluate.",
            }
        },
        "required": ["expression"],
    },
}

# Whitelist of safe names available in expressions
SAFE_GLOBALS = {
    "__builtins__": {},
    "math": math,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
}


def run(expression: str) -> str:
    try:
        # Parse and validate the AST before evaluating
        tree = ast.parse(expression, mode="eval")
        _validate_ast(tree)
        result = eval(compile(tree, "<string>", "eval"), SAFE_GLOBALS)  # noqa: S307
        return f"{expression} = {result}"
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as e:
        return f"Math error: {e}"
    except SyntaxError:
        return f"Invalid expression syntax: {expression}"


def _validate_ast(tree: ast.AST) -> None:
    """Block any AST nodes that could be dangerous."""
    allowed_node_types = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call,
        ast.Constant, ast.Name, ast.Attribute,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.Mod, ast.FloorDiv, ast.USub, ast.UAdd,
        ast.Load,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_node_types):
            raise ValueError(f"Unsafe operation in expression: {type(node).__name__}")
