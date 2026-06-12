"""
Advanced — Logger
==================
Adds two new panels on top of the Simple logger:

  log_plan(plan)
  ──────────────
  Shown before the ReAct loop starts. Displays the agent's numbered plan in
  a magenta panel so you can see its intent before it acts.

  log_token_usage(input_tokens, output_tokens)
  ─────────────────────────────────────────────
  Shown at the end of every run. Displays total tokens consumed and an
  estimated cost in USD based on Claude Sonnet 4 pricing.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def log_think(content: str) -> None:
    console.print(Panel(content, title="[bold blue]🧠 THINK[/bold blue]", border_style="blue"))


def log_act(tool_name: str, tool_input: dict) -> None:
    text = Text()
    text.append(f"Tool: {tool_name}\n", style="bold yellow")
    text.append(str(tool_input), style="dim")
    console.print(Panel(text, title="[bold yellow]⚡ ACT[/bold yellow]", border_style="yellow"))


def log_observe(result: str, is_error: bool = False) -> None:
    style = "red" if is_error else "green"
    label = "❌ ERROR" if is_error else "👁 OBSERVE"
    console.print(Panel(result[:500], title=f"[bold {style}]{label}[/bold {style}]", border_style=style))


def log_finish(answer: str) -> None:
    console.print(Panel(answer, title="[bold green]✅ FINAL ANSWER[/bold green]", border_style="green"))


def log_step(step: int, max_steps: int) -> None:
    console.rule(f"[dim]Step {step}/{max_steps}[/dim]")


# ── NEW: plan display ─────────────────────────────────────────────────────────

def log_plan(plan: str) -> None:
    """Show the agent's numbered plan before the ReAct loop begins."""
    console.print(Panel(plan, title="[bold magenta]📋 PLAN[/bold magenta]", border_style="magenta"))


# ── NEW: token usage tracker ──────────────────────────────────────────────────

_INPUT_COST_PER_M = 3.0    # USD per million input tokens  (Claude Sonnet 4)
_OUTPUT_COST_PER_M = 15.0  # USD per million output tokens


def log_token_usage(input_tokens: int, output_tokens: int) -> None:
    """Display cumulative token counts and estimated cost for the run."""
    input_cost = input_tokens / 1_000_000 * _INPUT_COST_PER_M
    output_cost = output_tokens / 1_000_000 * _OUTPUT_COST_PER_M

    text = (
        f"Input tokens:  {input_tokens:,}   (${input_cost:.4f})\n"
        f"Output tokens: {output_tokens:,}   (${output_cost:.4f})\n"
        f"Estimated cost: ${input_cost + output_cost:.4f}"
    )
    console.print(Panel(text, title="[bold dim]💰 TOKEN USAGE[/bold dim]", border_style="dim"))
