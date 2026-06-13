"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 4 — INTERMEDIATE: Prompt Position Ablation Study        ║
║  Topic: Lost-in-the-Middle + Attention Dilution, Measured Live  ║
╚══════════════════════════════════════════════════════════════════╝

You will run a controlled experiment to MEASURE how the position
and density of a critical formatting rule affects model compliance.

This lesson produces a data table you can discuss in class.

Run: python lesson_04_position_ablation.py
Prereq: pip install google-generativeai pandas
        $env:GEMINI_API_KEY = "your-key-here"
"""

import os, json, re, time
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────────
# STEP 1 ▶ The Filler Content (simulates a realistic enterprise prompt)
# ─────────────────────────────────────────────────────────────────

FILLER = [
    "Always maintain a professional and respectful tone.",
    "Do not reveal confidential company information.",
    "If unsure, escalate to a senior team member.",
    "Adhere to all data privacy regulations including GDPR.",
    "Keep responses concise and under 150 words.",
    "Format all dates as DD/MM/YYYY.",
    "Acknowledge the user's query before answering.",
    "Suggest further resources when applicable.",
    "Avoid speculative or unverified information.",
    "End every response with: 'Is there anything else I can help with?'",
]

# ─────────────────────────────────────────────────────────────────
# STEP 2 ▶ The Critical Rule we want the model to follow
# ─────────────────────────────────────────────────────────────────

CRITICAL_RULE = (
    "WEATHER TOOL RULE: For any weather query, output ONLY this JSON "
    "and nothing else:\n"
    '{"tool":"get_weather","parameters":{"location":"<city>","unit":"celsius"}}'
)

# ─────────────────────────────────────────────────────────────────
# STEP 3 ▶ Build Prompts with the Rule at Different Positions
# ─────────────────────────────────────────────────────────────────

def build_prompt(position: str, num_fillers: int) -> str:
    """
    Place CRITICAL_RULE at:
      - "start"  → rule first, filler after
      - "middle" → half filler, rule, half filler
      - "end"    → filler first, rule last
    """
    fillers = FILLER[:num_fillers]
    half    = num_fillers // 2

    if position == "start":
        return CRITICAL_RULE + "\n\n" + "\n".join(fillers)
    elif position == "middle":
        before = "\n".join(fillers[:half])
        after  = "\n".join(fillers[half:])
        return before + "\n\n" + CRITICAL_RULE + "\n\n" + after
    elif position == "end":
        return "\n".join(fillers) + "\n\n" + CRITICAL_RULE
    else:
        raise ValueError(f"Unknown position: {position}")

# ─────────────────────────────────────────────────────────────────
# STEP 4 ▶ Scorer
# ─────────────────────────────────────────────────────────────────

def score_compliance(text: str, expected_city: str) -> dict:
    """
    Scores:
      - pure_json : model output is ONLY JSON, no prose
      - tool_ok   : tool name correct
      - city_ok   : correct city
    """
    result = {"pure_json": False, "tool_ok": False, "city_ok": False, "score": 0}
    text = text.strip()

    # Check if it's pure JSON (no surrounding prose)
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        json_str = m.group(1)
        non_json = text.replace(json_str, "").strip()
        result["pure_json"] = len(non_json) < 10  # allow tiny whitespace
        try:
            data = json.loads(json_str)
            if data.get("tool") == "get_weather":
                result["tool_ok"] = True
                result["score"] += 40
            if data.get("parameters", {}).get("location","").lower() == expected_city.lower():
                result["city_ok"] = True
                result["score"] += 40
            if result["pure_json"]:
                result["score"] += 20
        except json.JSONDecodeError:
            pass
    return result

# ─────────────────────────────────────────────────────────────────
# STEP 5 ▶ Run the Ablation Grid
# ─────────────────────────────────────────────────────────────────

POSITIONS    = ["start", "middle", "end"]
FILLER_SIZES = [2, 5, 10]   # dilution levels: low, medium, high
QUERIES      = [
    {"q": "What's the weather in Amsterdam?", "city": "Amsterdam"},
    {"q": "Check the weather in Nairobi.",     "city": "Nairobi"},
]

def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[!] Set GEMINI_API_KEY to run this lesson.")
        return

    genai.configure(api_key=api_key)

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  LESSON 4: LOST-IN-THE-MIDDLE — Position Ablation Experiment    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\n  Grid: {len(POSITIONS)} positions × {len(FILLER_SIZES)} dilution levels × {len(QUERIES)} queries")
    print(f"  Total API calls: {len(POSITIONS) * len(FILLER_SIZES) * len(QUERIES)}\n")

    results_table = []

    for n_fill in FILLER_SIZES:
        for pos in POSITIONS:
            prompt = build_prompt(pos, n_fill)
            model  = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=prompt
            )
            total_score = 0

            for case in QUERIES:
                try:
                    resp  = model.generate_content(case["q"])
                    text  = resp.text.strip()
                    s     = score_compliance(text, case["city"])
                    total_score += s["score"]
                    time.sleep(1)
                except Exception as e:
                    print(f"  [Error] {e}")

            avg = total_score / len(QUERIES)
            results_table.append({
                "Position":   pos.upper(),
                "Filler Lines": n_fill,
                "Avg Score":  f"{avg:.0f}%",
                "Dilution":   "Low" if n_fill == 2 else "Med" if n_fill == 5 else "High",
            })
            print(f"  pos={pos:<6}  fillers={n_fill:>2}  → avg={avg:.0f}%")

    # ── Results Grid ──
    print(f"\n{'═'*62}")
    print("  RESULTS TABLE: Score by Position × Dilution Level")
    print(f"{'═'*62}")
    print(f"  {'Position':<10}  {'Dilution':<8}  {'Filler Lines':<14}  Score")
    print(f"  {'─'*58}")
    for row in results_table:
        bar = "▓" * (int(row["Avg Score"].replace("%","")) // 10)
        print(f"  {row['Position']:<10}  {row['Dilution']:<8}  {row['Filler Lines']:<14}  {row['Avg Score']:<6}  {bar}")

    print(f"""
{'═'*62}
  WHAT YOU SHOULD SEE
{'═'*62}
  • END position scores HIGHEST across all dilution levels
    → Recency bias: the model attends strongly to the last tokens
    → The critical rule is closest to the generation point

  • MIDDLE scores LOWEST, especially with High dilution
    → Liu et al. 2023: "Lost in the Middle" — U-shaped recall

  • START scores second — primacy effect
    → The model's context window starts fresh at position 0

  DESIGN RULE: Place critical constraints at the END of the
  system prompt, immediately before the user message.
{'═'*62}
""")

    print("""
╔══════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Add a 4th position: "repeated" — place the rule at      ║
║     BOTH start and end. Does it outscore all others?        ║
║                                                             ║
║  2. Plot the results table as a heatmap using matplotlib:   ║
║     x-axis = position, y-axis = dilution, color = score     ║
║                                                             ║
║  3. Increase FILLER_SIZES to [2, 5, 10, 20, 50]. At what   ║
║     dilution level does even the END position start failing?║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    run()
