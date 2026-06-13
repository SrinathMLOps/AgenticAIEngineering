import sys
from agent.loop import run_agent
from rich.console import Console
from rich.prompt import Prompt

console = Console()

EXAMPLE_TASKS = [
    # Original tools
    "What is 15% of 847, and what is the square root of that result? Show all workings.",
    "Calculate compound interest on £1000 at 5% annual rate for 10 years. Show year-by-year breakdown.",
    # New: weather tool
    "What is the current weather in Tokyo, Japan? Give me a 3-day forecast.",
    "Compare today's weather in London and New York — which city is warmer right now?",
    # New: Wikipedia tool
    "Use Wikipedia to find out who invented the World Wide Web and when. Save the answer to www_history.txt",
    "Look up the Python programming language on Wikipedia. When was it first released and who created it?",
    # Longer research task (uses the raised MAX_STEPS)
    "Search the web for the 3 most-used programming languages in 2024, look each one up on Wikipedia "
    "for its origin year, then save a ranked summary to languages.txt",
]


def run_interactive() -> None:
    console.print("\n[bold]Simple ReAct Agent[/bold]  [dim](weather + wikipedia tools)[/dim]")
    console.print("[dim]Type a task or choose from the examples below[/dim]\n")

    for i, task in enumerate(EXAMPLE_TASKS, 1):
        console.print(f"  [cyan]{i}.[/cyan] {task[:90]}{'…' if len(task) > 90 else ''}")

    console.print()
    choice = Prompt.ask("Enter task number or type your own task")

    if choice.isdigit() and 1 <= int(choice) <= len(EXAMPLE_TASKS):
        task = EXAMPLE_TASKS[int(choice) - 1]
    else:
        task = choice

    console.print(f"\n[bold green]Task:[/bold green] {task}\n")
    run_agent(task)


def run_single(task: str) -> None:
    console.print(f"\n[bold green]Task:[/bold green] {task}\n")
    run_agent(task)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_single(" ".join(sys.argv[1:]))
    else:
        run_interactive()
