"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 5 — ADVANCED: Multi-Agent Orchestration                 ║
║  Topic: Planner + Executor + Critic Agent Pipeline              ║
╚══════════════════════════════════════════════════════════════════╝

You will build a 3-agent system where:
  - PLANNER: Breaks the user goal into sub-tasks + decides which tools to call
  - EXECUTOR: Executes each sub-task by calling real tools
  - CRITIC:   Reviews the full execution trace for errors / missing steps

All three agents use Gemini API with different system prompts,
demonstrating how prompt architecture shapes each agent's behavior.

Run: python lesson_05_multi_agent.py
Prereq: pip install google-generativeai
        $env:GEMINI_API_KEY = "your-key-here"
"""

import os, json, time
import google.generativeai as genai
from google.generativeai import types

# ─────────────────────────────────────────────────────────────────
# TOOLS (shared across agents)
# ─────────────────────────────────────────────────────────────────

WEATHER_DATA = {
    "london":  {"temp_c": 14, "condition": "Cloudy",  "humidity": 72},
    "tokyo":   {"temp_c": 28, "condition": "Sunny",   "humidity": 55},
    "new york":{"temp_c": 22, "condition": "Partly Cloudy", "humidity": 61},
    "dubai":   {"temp_c": 41, "condition": "Very Hot","humidity": 30},
    "sydney":  {"temp_c": 18, "condition": "Rainy",   "humidity": 80},
    "berlin":  {"temp_c": 11, "condition": "Overcast","humidity": 68},
    "paris":   {"temp_c": 17, "condition": "Clear",   "humidity": 58},
}

RATES = {"usd_eur":0.92,"usd_gbp":0.79,"usd_jpy":157.4,"usd_inr":83.5,
         "eur_usd":1.09,"gbp_usd":1.27,"jpy_usd":0.0064,"inr_usd":0.012}

def get_weather(city: str, unit: str = "celsius") -> dict:
    d = WEATHER_DATA.get(city.lower())
    if not d: return {"error": f"No data for {city}"}
    t = d["temp_c"] if unit == "celsius" else round(d["temp_c"]*9/5+32,1)
    return {"city": city.title(), "temperature": t, "unit": unit,
            "condition": d["condition"], "humidity": f"{d['humidity']}%"}

def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
    r = RATES.get(f"{from_curr.lower()}_{to_curr.lower()}")
    if not r: return {"error": f"No rate {from_curr}→{to_curr}"}
    return {"original": f"{amount} {from_curr.upper()}",
            "converted": f"{round(amount*r,2)} {to_curr.upper()}", "rate": r}

def get_city_info(city: str) -> dict:
    DB = {"london":{"country":"UK","tz":"GMT+1","lang":"English"},
          "tokyo": {"country":"Japan","tz":"GMT+9","lang":"Japanese"},
          "paris": {"country":"France","tz":"GMT+2","lang":"French"},
          "dubai": {"country":"UAE","tz":"GMT+4","lang":"Arabic"},
          "berlin":{"country":"Germany","tz":"GMT+2","lang":"German"},
          "sydney":{"country":"Australia","tz":"GMT+10","lang":"English"}}
    d = DB.get(city.lower())
    if not d: return {"error": f"No info for {city}"}
    return {"city": city.title(), **d}

TOOL_MAP = {"get_weather": get_weather,
            "convert_currency": convert_currency,
            "get_city_info": get_city_info}

TOOL_SCHEMA = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="get_weather",
        description="Get weather for a city",
        parameters=types.Schema(type=types.Type.OBJECT,
            properties={"city":  types.Schema(type=types.Type.STRING),
                        "unit":  types.Schema(type=types.Type.STRING)},
            required=["city"])
    ),
    types.FunctionDeclaration(
        name="convert_currency",
        description="Convert money between currencies",
        parameters=types.Schema(type=types.Type.OBJECT,
            properties={"amount":    types.Schema(type=types.Type.NUMBER),
                        "from_curr": types.Schema(type=types.Type.STRING),
                        "to_curr":   types.Schema(type=types.Type.STRING)},
            required=["amount","from_curr","to_curr"])
    ),
    types.FunctionDeclaration(
        name="get_city_info",
        description="Get country, timezone, language for a city",
        parameters=types.Schema(type=types.Type.OBJECT,
            properties={"city": types.Schema(type=types.Type.STRING)},
            required=["city"])
    ),
])

# ─────────────────────────────────────────────────────────────────
# AGENT IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────

# ── Agent 1: PLANNER ─────────────────────────────────────────────
PLANNER_PROMPT = """You are a task planner for an agentic AI system.

Given a user's goal, you must output a JSON plan listing each sub-task.
Available tools: get_weather, convert_currency, get_city_info

Output ONLY a JSON array like this:
[
  {"step": 1, "tool": "get_weather",      "args": {"city": "Paris", "unit": "celsius"}},
  {"step": 2, "tool": "convert_currency", "args": {"amount": 100, "from_curr": "USD", "to_curr": "EUR"}},
  {"step": 3, "tool": "get_city_info",    "args": {"city": "Paris"}}
]

If no tool is needed, output: []
Do NOT include any text outside the JSON array."""


def planner_agent(user_goal: str, model: genai.GenerativeModel) -> list:
    """Returns a list of tool-call steps to execute."""
    resp = model.generate_content(user_goal)
    text = resp.text.strip()
    # Strip markdown code block if present
    text = text.replace("```json","").replace("```","").strip()
    try:
        plan = json.loads(text)
        assert isinstance(plan, list)
        return plan
    except Exception:
        return []


# ── Agent 2: EXECUTOR ────────────────────────────────────────────
def executor_agent(plan: list) -> list:
    """Executes each step in the plan and collects results."""
    results = []
    for step in plan:
        tool_name = step.get("tool")
        args      = step.get("args", {})
        fn        = TOOL_MAP.get(tool_name)
        if fn:
            result = fn(**args)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        results.append({
            "step":   step["step"],
            "tool":   tool_name,
            "args":   args,
            "result": result,
        })
    return results


# ── Agent 3: CRITIC ──────────────────────────────────────────────
CRITIC_PROMPT = """You are a quality-checking critic for an agentic AI system.

You receive:
  1. The user's original goal
  2. The execution trace (which tools were called and their results)

Your job:
  - Check if the user's goal was FULLY addressed
  - Flag any errors or missing steps
  - Write a short final answer summarizing the results for the user

Format your response as:
STATUS: [COMPLETE | INCOMPLETE | ERROR]
ISSUES: <any problems found, or "None">
ANSWER: <clean, friendly summary of results for the user>"""


def critic_agent(user_goal: str, trace: list, model: genai.GenerativeModel) -> str:
    """Reviews the execution and writes the final user-facing answer."""
    context = (
        f"User Goal: {user_goal}\n\n"
        f"Execution Trace:\n{json.dumps(trace, indent=2)}"
    )
    resp = model.generate_content(context)
    return resp.text.strip()


# ─────────────────────────────────────────────────────────────────
# STEP 4 ▶ Orchestrator — Runs the full pipeline
# ─────────────────────────────────────────────────────────────────

def run_pipeline(user_goal: str, api_key: str):
    genai.configure(api_key=api_key)

    planner_model = genai.GenerativeModel("gemini-1.5-flash",
                                          system_instruction=PLANNER_PROMPT)
    critic_model  = genai.GenerativeModel("gemini-1.5-flash",
                                          system_instruction=CRITIC_PROMPT)

    print(f"\n  ╔{'═'*60}╗")
    print(f"  ║  GOAL: {user_goal[:55]:<55}  ║")
    print(f"  ╚{'═'*60}╝")

    # Stage 1: Plan
    print("\n  [PLANNER] Generating task plan...")
    plan = planner_agent(user_goal, planner_model)
    if not plan:
        print("  [PLANNER] No tools needed or plan failed.")
        return
    for step in plan:
        print(f"  → Step {step['step']}: {step['tool']}({step.get('args',{})})")

    # Stage 2: Execute
    print("\n  [EXECUTOR] Running tools...")
    trace = executor_agent(plan)
    for t in trace:
        status = "✓" if "error" not in t["result"] else "✗"
        print(f"  {status} {t['tool']}  → {json.dumps(t['result'])[:80]}")

    # Stage 3: Critique & Summarise
    print("\n  [CRITIC] Reviewing trace and composing answer...")
    answer = critic_agent(user_goal, trace, critic_model)
    print(f"\n{answer}\n")
    return answer


# ─────────────────────────────────────────────────────────────────
# EXERCISES
# ─────────────────────────────────────────────────────────────────

GOALS = [
    "I'm flying to Tokyo. Tell me the weather and how much is 500 USD in JPY.",
    "Compare the weather in Berlin and Dubai, and tell me the local language in each.",
    "Plan my Paris trip: local language, current weather, and convert 200 GBP to EUR.",
]

def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[!] Set GEMINI_API_KEY to run this lesson.")
        return

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  LESSON 5: MULTI-AGENT PIPELINE — Planner + Executor + Critic   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    for goal in GOALS:
        run_pipeline(goal, api_key)
        time.sleep(2)

    print("""
╔══════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Add a MEMORY layer: store all tool results in a dict    ║
║     so the CRITIC can reference previous run results in     ║
║     the same session.                                       ║
║                                                             ║
║  2. Add a RETRY mechanism to the EXECUTOR: if a tool        ║
║     returns {"error": ...}, the executor should ask the     ║
║     planner to replan that step.                            ║
║                                                             ║
║  3. Change the CRITIC prompt to output the answer in        ║
║     JSON instead of plain text. Parse and display it        ║
║     in a formatted table.                                   ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    run()
