"""
Simple — Logger
================
Plain coloured terminal output using the Rich library.
No token tracking, no plan display — that's added in later levels.
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
