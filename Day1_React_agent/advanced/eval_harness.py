"""
Advanced — Eval Harness
========================
Run: python eval_harness.py

Evaluates the agent on 5 benchmark tasks, prints a pass/fail table, and
saves the full results to eval_results.json.

How it works:
  1. Each task has a task string and a check() function.
  2. run_agent() is called for each task in isolation (cache cleared between runs).
  3. check(answer) returns True/False — pass if True, fail if False.
  4. Accuracy = passed / total * 100.

This is the simplest possible eval harness. Real evals use larger task sets,
human-verified gold answers, and automated scoring with a judge model.
"""
import json
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agent.loop import run_agent
from tools.registry import clear_cache  # caching is an Advanced feature

# ---------------------------------------------------------------------------
# Benchmark tasks
# ---------------------------------------------------------------------------
EVAL_TASKS = [
    {
        "id": 1,
        "description": "Calculator: sqrt(1764) == 42",
        "task": "What is the square root of 1764? Use the calculator tool.",
        "check": lambda ans: "42" in ans,
    },
    {
        "id": 2,
        "description": "Calculator: 15% of 847 == 127.05",
        "task": "What is exactly 15% of 847? Use the calculator and show the result.",
        "check": lambda ans: "127.05" in ans,
    },
    {
        "id": 3,
        "description": "File I/O: write sentinel string to eval_check.txt",
        "task": "Write exactly the text 'eval_test_passed' (nothing else) to a file called eval_check.txt",
        "check": lambda _: (
            Path("eval_check.txt").exists()
            and "eval_test_passed" in Path("eval_check.txt").read_text(encoding="utf-8")
        ),
    },
    {
        "id": 4,
        "description": "Wikipedia: Python first released in 1991",
        "task": (
            "Use the wikipedia_search tool to look up 'Python programming language' "
            "and tell me what year it was first released."
        ),
        "check": lambda ans: "1991" in ans,
    },
    {
        "id": 5,
        "description": "Calculator: 2^10 == 1024",
        "task": "What is 2 to the power of 10? Use the calculator tool.",
        "check": lambda ans: "1024" in ans,
    },
]


def run_eval() -> None:
    results = []

    print("\n" + "=" * 60)
    print("  EVAL HARNESS  —  5-task benchmark")
    print("=" * 60)

    for t in EVAL_TASKS:
        print(f"\n[Task {t['id']}]  {t['description']}")
        print("-" * 50)

        # Reset the tool cache so each task starts cold (fair comparison)
        clear_cache()

        start = time.time()
        try:
            answer = run_agent(t["task"])
            passed = bool(t["check"](answer))
        except Exception as exc:
            answer = f"ERROR: {exc}"
            passed = False
        elapsed = round(time.time() - start, 1)

        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"\n  → {status}  ({elapsed}s)")

        results.append(
            {
                "id": t["id"],
                "description": t["description"],
                "passed": passed,
                "elapsed_s": elapsed,
            }
        )

    # ── Summary ──────────────────────────────────────────────────────────────
    passed_count = sum(1 for r in results if r["passed"])
    accuracy = passed_count / len(results) * 100

    print("\n" + "=" * 60)
    print(f"  RESULTS:  {passed_count}/{len(results)} passed  ({accuracy:.0f}% accuracy)")
    print("=" * 60)
    for r in results:
        icon = "✓" if r["passed"] else "✗"
        print(f"  [{icon}]  Task {r['id']}: {r['description']}  ({r['elapsed_s']}s)")

    # ── Persist log ───────────────────────────────────────────────────────────
    log_path = "eval_results.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "accuracy_pct": accuracy,
                "passed": passed_count,
                "total": len(results),
                "tasks": results,
            },
            f,
            indent=2,
        )
    print(f"\n  Log saved → {log_path}\n")


if __name__ == "__main__":
    run_eval()
