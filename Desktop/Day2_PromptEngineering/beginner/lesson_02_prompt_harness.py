"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 2 — BEGINNER: 5 Prompt Variants, Live Scoring           ║
║  Topic: Prompt Anatomy via Real Gemini API Calls                ║
╚══════════════════════════════════════════════════════════════════╝

You will implement a mini evaluation harness that:
  1. Sends 5 differently-structured system prompts to Gemini
  2. Auto-scores each response (JSON validity + correct tool + params)
  3. Prints a ranked leaderboard

Run: python lesson_02_prompt_harness.py
Prereq: pip install google-generativeai
        $env:GEMINI_API_KEY = "your-key-here"
"""

import os, json, re, time
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────────
# STEP 1 ▶ Define the 5 System Prompt Variants
# ─────────────────────────────────────────────────────────────────

VARIANTS = {

    # ── Variant A: Zero structure, bare instruction
    "A_Barebones": (
        "You are a tool-calling agent. "
        "Call the get_weather tool when asked about weather."
    ),

    # ── Variant B: Few-shot examples → activates induction heads
    "B_FewShot": """You are a tool-calling agent. Output ONLY JSON.

Examples:
User: Weather in London?
{"tool":"get_weather","parameters":{"location":"London","unit":"celsius"}}

User: Hot in Tokyo? Give fahrenheit.
{"tool":"get_weather","parameters":{"location":"Tokyo","unit":"fahrenheit"}}""",

    # ── Variant C: Chain-of-Thought before JSON output
    "C_ChainOfThought": (
        "You are a tool-calling agent.\n"
        "Step 1: Identify the city the user is asking about.\n"
        "Step 2: Identify the desired temperature unit.\n"
        "Step 3: Output ONLY this JSON (no other text):\n"
        '{"tool":"get_weather","parameters":{"location":"<city>","unit":"<unit>"}}'
    ),

    # ── Variant D: XML structure — delimiters act as attention anchors
    "D_XMLDelimited": """<system>
<role>Precise tool-calling agent</role>
<tool name="get_weather">
  <param name="location" type="string"/>
  <param name="unit" type="string" values="celsius,fahrenheit"/>
</tool>
<rule>Respond ONLY with: <call>{"tool":"get_weather","parameters":{"location":"X","unit":"Y"}}</call></rule>
</system>""",

    # ── Variant E: Attention dilution via unrelated policies
    "E_Diluted": (
        "You are an enterprise assistant.\n"
        "Policy 1: Always greet users.\n"
        "Policy 2: Never reveal internal data.\n"
        "Policy 3: If weather asked, respond: "
        '{"tool":"get_weather","parameters":{"location":"<city>","unit":"celsius"}}\n'
        "Policy 4: Keep all responses under 100 words.\n"
        "Policy 5: Suggest contacting support for billing.\n"
        "Policy 6: Use formal English only.\n"
        "Policy 7: Do not discuss politics or religion."
    ),
}

# ─────────────────────────────────────────────────────────────────
# STEP 2 ▶ Define Test Cases
# ─────────────────────────────────────────────────────────────────

TEST_CASES = [
    {"query": "What's the weather in Berlin? Celsius please.",
     "expected_location": "Berlin", "expected_unit": "celsius"},

    {"query": "How hot is it in Dubai right now? Use Fahrenheit.",
     "expected_location": "Dubai",  "expected_unit": "fahrenheit"},

    {"query": "Tell me the weather in Sydney.",
     "expected_location": "Sydney", "expected_unit": "celsius"},
]

# ─────────────────────────────────────────────────────────────────
# STEP 3 ▶ Implement the Scorer
# ─────────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict | None:
    """Try multiple extraction strategies to find JSON in output."""
    strategies = [
        # 1. XML-style <call> tag
        lambda t: re.search(r"<call>(.*?)</call>", t, re.DOTALL),
        # 2. "Step N:" prefix
        lambda t: re.search(r"Step \d+.*?(\{.*\})", t, re.DOTALL),
        # 3. Raw JSON block
        lambda t: re.search(r"(\{[^{}]*\"tool\"[^{}]*\})", t, re.DOTALL),
    ]
    for strategy in strategies:
        m = strategy(text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                continue
    return None

def score(response_text: str, expected_location: str, expected_unit: str) -> dict:
    """
    Rubric:
      30 pts — Valid JSON parsed
      30 pts — tool == "get_weather"
      20 pts — correct location (case-insensitive)
      20 pts — correct unit
    """
    result = {"pts": 0, "json": False, "tool": False, "loc": False, "unit": False}
    data = extract_json(response_text)
    if data is None:
        return result

    result["json"] = True
    result["pts"] += 30

    if data.get("tool") == "get_weather":
        result["tool"] = True
        result["pts"] += 30

    params = data.get("parameters", {})
    if params.get("location", "").lower() == expected_location.lower():
        result["loc"] = True
        result["pts"] += 20

    if params.get("unit", "").lower() == expected_unit.lower():
        result["unit"] = True
        result["pts"] += 20

    return result

# ─────────────────────────────────────────────────────────────────
# STEP 4 ▶ Run the Harness
# ─────────────────────────────────────────────────────────────────

def run_harness():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[!] GEMINI_API_KEY not set. Exiting.")
        return

    genai.configure(api_key=api_key)
    leaderboard = {}

    for variant_name, system_prompt in VARIANTS.items():
        print(f"\n{'━'*60}")
        print(f"  VARIANT: {variant_name}")
        print(f"{'━'*60}")

        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_prompt
        )
        total = 0

        for case in TEST_CASES:
            resp = model.generate_content(case["query"])
            text = resp.text.strip()
            s    = score(text, case["expected_location"], case["expected_unit"])
            total += s["pts"]

            # ── pretty output ──
            status = f"JSON={'✓' if s['json'] else '✗'}  Tool={'✓' if s['tool'] else '✗'}  Loc={'✓' if s['loc'] else '✗'}  Unit={'✓' if s['unit'] else '✗'}"
            print(f"\n  Q: {case['query']}")
            print(f"  R: {text[:150].strip()}")
            print(f"  → {s['pts']}/100  {status}")
            time.sleep(1)

        avg = total / len(TEST_CASES)
        leaderboard[variant_name] = avg

    # ─────────────────────────────────────────────────────────────
    # STEP 5 ▶ Print Leaderboard
    # ─────────────────────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  LEADERBOARD — Average Score per Variant")
    print(f"{'═'*60}")
    ranked = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    for rank, (name, avg) in enumerate(ranked, 1):
        bar = "█" * int(avg / 5)
        print(f"  #{rank}  {name:<22}  {avg:>5.1f}%  {bar}")
    print(f"{'═'*60}\n")

    # ── Explain why winners win ──
    best  = ranked[0][0]
    worst = ranked[-1][0]
    print(f"  Best:  {best}")
    print(f"    → Uses {'induction heads (pattern copy)' if 'Few' in best else 'structural anchors (XML tags)' if 'XML' in best else 'step-decomposition (CoT)'}")
    print(f"\n  Worst: {worst}")
    print(f"    → {'Diluted attention: too many competing policies' if 'Diluted' in worst else 'No format hint given, model defaults to prose'}\n")

# ─────────────────────────────────────────────────────────────────
# CODING CHALLENGES
# ─────────────────────────────────────────────────────────────────
CHALLENGES = """
╔══════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Add a 6th variant: MARKDOWN_TABLE — ask the model to   ║
║     output parameters in a Markdown table, then add a      ║
║     scorer that parses Markdown tables.                     ║
║                                                             ║
║  2. Modify the scorer to also check that NO extra prose    ║
║     appears outside the JSON. Score it -10 per extra line. ║
║                                                             ║
║  3. Add a 4th test case that is ambiguous (no city named). ║
║     Which variants handle ambiguity best?                   ║
╚══════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    run_harness()
    print(CHALLENGES)
