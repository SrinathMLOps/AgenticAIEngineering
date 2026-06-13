import sys
from agent.loop import run_agent
from rich.console import Console
from rich.prompt import Prompt

console = Console()

EXAMPLE_TASKS = [
    # Plan-first: agent plans 3–5 steps then executes — good to see the plan panel
    "Research the history of artificial intelligence: when it started, key milestones, "
    "and current state. Save a structured report to ai_history.txt",
    # Caching: agent may verify the same Wikipedia article twice — second call is instant
    "Compare Python and JavaScript: look up each on Wikipedia, search for their current "
    "popularity rankings, and save a comparison table to languages_comparison.txt",
    # Plan + weather + Wikipedia + calculator
    "Look up what latitude London is at, then use the calculator to work out how many km "
    "north of the equator it is (1 degree latitude ≈ 111 km). Also fetch today's weather.",
    # Multi-step planning test
    "Find the current population of the 3 most populous countries, calculate what percentage "
    "of world population (8.1 billion) each represents, and save results to population.txt",
    # Eval harness tasks (same tasks used by eval_harness.py)
    "What is the square root of 1764? Use the calculator tool.",
]


def run_interactive() -> None:
    console.print("\n[bold]Advanced ReAct Agent[/bold]  "
                  "[dim](plan-first · caching · streaming · retry · token tracker)[/dim]")
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
