import sys
from agent.loop import run_agent
from rich.console import Console
from rich.prompt import Prompt

console = Console()

EXAMPLE_TASKS = [
    # Streaming: you'll see the reasoning appear token-by-token
    "Explain how HTTPS works, step by step. Search if you need to verify details.",
    # Retry: search can occasionally time out — retry handles it silently
    "Search for the top 5 Python web frameworks in 2024 and summarise each in one sentence.",
    # Token tracker: a multi-step research task shows real cost
    "Look up the history of the internet on Wikipedia, then search for its current size "
    "in terms of websites. Save a combined summary to internet_facts.txt",
    # Weather + cost visibility
    "Get the weather forecast for the next 3 days in Sydney, Australia. "
    "Also tell me what season it currently is there and why.",
    # Calculator chain — multiple tool calls → visible token growth
    "A rectangle has sides of 14.7 cm and 23.1 cm. Calculate its area, perimeter, "
    "and the length of its diagonal. Show all calculations.",
]


def run_interactive() -> None:
    console.print("\n[bold]Intermediate ReAct Agent[/bold]  "
                  "[dim](streaming · retry · token tracker)[/dim]")
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
