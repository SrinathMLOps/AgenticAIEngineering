"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 7 — JSON PROMPTING MASTERY                              ║
║  Topic: Getting Reliable JSON from LLMs + Validation & Repair   ║
╚══════════════════════════════════════════════════════════════════╝

Why JSON? In agentic AI, JSON is the universal language:
  - Tool call parameters → JSON
  - Structured data extraction → JSON
  - Agent-to-agent messages → JSON
  - RAG metadata → JSON

LLMs are NOT guaranteed to produce valid JSON. This lesson covers
5 techniques to reliably extract JSON and build a self-healing
validation loop that auto-repairs malformed output.

Run: python lesson_07_json_prompting.py
Prereq: pip install google-generativeai
        $env:GEMINI_API_KEY = "your-key-here"
"""

import os, json, re, time
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────────
# PART 1 ▶ Why JSON Breaks — Common LLM Failure Modes
# ─────────────────────────────────────────────────────────────────
# LLMs fail at JSON for predictable, attention-driven reasons:
#
#  1. Trailing commas     → {"a":1,"b":2,}   (common in training data)
#  2. Single quotes       → {'key': 'val'}   (Python dict syntax leak)
#  3. Prose wrapping      → "Here is the JSON: {...}"
#  4. Markdown fencing    → ```json\n{...}\n```
#  5. Truncation          → {"key": "very long val...  (incomplete)
#  6. Wrong nesting       → {"a": {"b": 1}  (missing closing brace)
#
# Your job as a prompt engineer: prevent these with structure,
# and recover from them with a validation + repair loop.

print("╔══════════════════════════════════════════════════════════════════╗")
print("║  LESSON 7: JSON PROMPTING MASTERY                               ║")
print("╚══════════════════════════════════════════════════════════════════╝")

# ─────────────────────────────────────────────────────────────────
# PART 2 ▶ JSON Extraction Utility (multi-strategy)
# ─────────────────────────────────────────────────────────────────

def extract_json(text: str):
    """
    Tries 5 strategies to extract JSON from raw LLM output.
    Returns parsed dict/list or None.
    """
    # Strategy 1: Strip markdown code fences
    text_clean = re.sub(r"```json\s*", "", text)
    text_clean = re.sub(r"```\s*", "", text_clean).strip()

    # Strategy 2: Direct parse of cleaned text
    try:
        return json.loads(text_clean)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Extract first {...} block
    m = re.search(r"(\{[\s\S]*\})", text_clean)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 4: Extract first [...] block (arrays)
    m = re.search(r"(\[[\s\S]*\])", text_clean)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 5: Fix trailing commas and try again
    fixed = re.sub(r",\s*([\}\]])", r"\1", text_clean)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return None


def validate_schema(data: dict, required_keys: list, types: dict = None) -> tuple:
    """
    Checks a parsed dict has required keys and correct value types.
    Returns (is_valid: bool, errors: list[str])
    """
    errors = []
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: '{key}'")
        elif types and key in types:
            expected_type = types[key]
            if not isinstance(data[key], expected_type):
                errors.append(
                    f"Key '{key}': expected {expected_type.__name__}, "
                    f"got {type(data[key]).__name__}"
                )
    return len(errors) == 0, errors


# ── Demo: Test extraction on intentionally broken JSON strings ──
BROKEN_SAMPLES = [
    '```json\n{"name": "Alice", "age": 30}\n```',
    "Here is the data: {\"city\": \"Paris\", \"temp\": 17}",
    "{'tool': 'get_weather', 'location': 'Berlin'}",   # single quotes — will fail
    '{"items": [1, 2, 3,]}',                           # trailing comma
    '{"status": "ok", "data": {"count": 5}',           # missing brace
]

print("\n  PART 2: JSON Extraction from Broken LLM Output")
print(f"  {'─'*60}")
for sample in BROKEN_SAMPLES:
    result = extract_json(sample)
    status = "✓ Recovered" if result else "✗ Failed   "
    print(f"  {status}  Input: {sample[:55].strip()}")
    if result:
        print(f"            → {result}")

print()

# ─────────────────────────────────────────────────────────────────
# PART 3 ▶ The 5 JSON Prompting Techniques (Live Gemini API)
# ─────────────────────────────────────────────────────────────────

TASK_CONTEXT = """
Extract structured data from the following user review:

Review: "I stayed at The Grand Palace Hotel in Rome for 3 nights last December.
The rooms were spacious and clean (4/5), but the breakfast was disappointing (2/5).
Overall rating: 3.5 out of 5. Would not return."
"""

REQUIRED_KEYS = ["hotel", "city", "duration_nights", "ratings", "would_return"]
KEY_TYPES     = {"hotel": str, "city": str, "duration_nights": int,
                 "ratings": dict, "would_return": bool}

TECHNIQUES = {

    # ── T1: Bare instruction (baseline, frequently fails) ──────
    "T1_Bare": (
        "You are a data extraction assistant. "
        "Extract information from the given text and return it as JSON."
    ),

    # ── T2: Schema-in-Prompt ───────────────────────────────────
    "T2_Schema": (
        "You are a data extraction assistant.\n"
        "Extract the following fields and return ONLY valid JSON — no prose, no markdown.\n\n"
        "Required JSON schema:\n"
        "{\n"
        '  "hotel":           string,\n'
        '  "city":            string,\n'
        '  "duration_nights": integer,\n'
        '  "ratings":         {"rooms": float, "breakfast": float, "overall": float},\n'
        '  "would_return":    boolean\n'
        "}"
    ),

    # ── T3: One-Shot Example ───────────────────────────────────
    "T3_OneShot": (
        "You are a data extraction assistant. Return ONLY JSON, no other text.\n\n"
        "Example:\n"
        'Input: "Stayed 2 nights at Hotel Mirage in Paris. Room: 5/5, Food: 4/5. '
        'Overall 4.5/5. Would return."\n'
        'Output: {"hotel":"Hotel Mirage","city":"Paris","duration_nights":2,'
        '"ratings":{"rooms":5.0,"food":4.0,"overall":4.5},"would_return":true}\n\n'
        "Now extract from the new input. Return ONLY JSON:"
    ),

    # ── T4: Chain-of-Thought → JSON ───────────────────────────
    "T4_CoT": (
        "You are a data extraction assistant.\n"
        "Step 1: Identify the hotel name.\n"
        "Step 2: Identify the city.\n"
        "Step 3: Identify the duration in nights (integer).\n"
        "Step 4: Extract individual ratings as floats.\n"
        "Step 5: Determine would_return as true or false.\n"
        "Step 6: Output ONLY the final JSON with these keys:\n"
        "hotel, city, duration_nights, ratings (dict), would_return (bool)\n"
        "NO text before or after the JSON."
    ),

    # ── T5: Constrained Prefix ────────────────────────────────
    # Force the model to start inside the JSON by ending the
    # prompt with the opening brace — the model must continue.
    "T5_ConstrainedPrefix": (
        "You are a data extraction assistant.\n"
        "Extract: hotel, city, duration_nights, ratings (dict of floats), would_return (bool).\n"
        "Complete the JSON below. Do not add any text before or after it:\n"
        "{"
    ),
}

# ─────────────────────────────────────────────────────────────────
# PART 4 ▶ Validation + Auto-Repair Loop
# ─────────────────────────────────────────────────────────────────

def repair_json(bad_text: str, model, schema_hint: str) -> dict | None:
    """
    If initial extraction fails schema validation, ask the model
    to repair its own output. This is the self-healing pattern.
    """
    repair_prompt = (
        f"The following JSON is either malformed or missing required fields:\n\n"
        f"{bad_text}\n\n"
        f"Required schema:\n{schema_hint}\n\n"
        "Output ONLY the corrected, complete, valid JSON. No other text."
    )
    try:
        resp = model.generate_content(repair_prompt)
        return extract_json(resp.text)
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────
# PART 5 ▶ Run Everything
# ─────────────────────────────────────────────────────────────────

def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[!] Set GEMINI_API_KEY to run the live sections.\n")
        return

    genai.configure(api_key=api_key)
    base_model = genai.GenerativeModel("gemini-1.5-flash")

    SCHEMA_HINT = (
        '{"hotel": string, "city": string, "duration_nights": int,\n'
        ' "ratings": {"rooms": float, "breakfast": float, "overall": float},\n'
        ' "would_return": bool}'
    )

    print("\n  PART 3 & 4: 5 Techniques — Live Gemini API")
    print(f"  {'─'*60}")

    leaderboard = {}

    for name, system_prompt in TECHNIQUES.items():
        print(f"\n  [{name}]")

        # Constrained prefix technique: append opening brace to user message
        if name == "T5_ConstrainedPrefix":
            user_msg = TASK_CONTEXT.strip() + "\n{"
        else:
            user_msg = TASK_CONTEXT.strip()

        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_prompt
        )
        try:
            resp  = model.generate_content(user_msg)
            text  = resp.text.strip()
            data  = extract_json(text)
            print(f"  Raw output: {text[:120].strip()}")

            if data:
                valid, errors = validate_schema(data, REQUIRED_KEYS, KEY_TYPES)
                if not valid:
                    print(f"  Schema errors: {errors}")
                    print(f"  Attempting auto-repair...")
                    data = repair_json(text, base_model, SCHEMA_HINT)
                    if data:
                        valid, errors = validate_schema(data, REQUIRED_KEYS, KEY_TYPES)

                if valid:
                    leaderboard[name] = "✅ Valid + Schema OK"
                    print(f"  Result: ✅ Valid JSON, schema correct")
                    print(f"  Data: {json.dumps(data, indent=2)[:200]}")
                else:
                    leaderboard[name] = f"⚠️  Parsed but schema issues: {errors[0]}"
                    print(f"  Result: ⚠️  Schema mismatch — {errors}")
            else:
                leaderboard[name] = "❌ Could not parse JSON"
                print(f"  Result: ❌ JSON extraction failed")

        except Exception as e:
            leaderboard[name] = f"❌ API Error: {e}"
            print(f"  Error: {e}")

        time.sleep(1.5)

    # ── Leaderboard ──
    print(f"\n{'═'*65}")
    print("  TECHNIQUE LEADERBOARD")
    print(f"{'═'*65}")
    for name, outcome in leaderboard.items():
        print(f"  {name:<28}  {outcome}")
    print(f"{'═'*65}")

    # ── Gemini Native JSON Mode (Best Practice) ──
    print("""
  BONUS: Gemini JSON Response Mode (Most Reliable)
  ─────────────────────────────────────────────────
  Gemini supports response_mime_type='application/json'
  which constrains the decoding to always produce valid JSON.
""")
    try:
        json_model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=(
                "Extract hotel, city, duration_nights, ratings (dict), would_return (bool) "
                "from the review. Return valid JSON only."
            ),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        resp = json_model.generate_content(TASK_CONTEXT.strip())
        parsed = json.loads(resp.text)
        print(f"  ✅ Gemini JSON Mode output:")
        print(f"  {json.dumps(parsed, indent=4)[:400]}")
    except Exception as e:
        print(f"  [Note] JSON mode test: {e}")


# ─────────────────────────────────────────────────────────────────
# CODING CHALLENGES
# ─────────────────────────────────────────────────────────────────
CHALLENGES = """
╔══════════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                              ║
╠══════════════════════════════════════════════════════════════════╣
║  1. JSON SCHEMA VALIDATOR                                       ║
║     Extend validate_schema() to also check:                     ║
║       - ratings values are between 0.0 and 5.0                 ║
║       - duration_nights is a positive integer                   ║
║       - hotel string is at least 3 characters                  ║
║                                                                 ║
║  2. MULTI-ROUND REPAIR                                          ║
║     Modify repair_json() to retry up to 3 times if the         ║
║     repaired JSON still fails schema validation.               ║
║     Track how many repair rounds each technique needed.        ║
║                                                                 ║
║  3. ARRAY EXTRACTION                                            ║
║     Change the task to: extract ALL hotels mentioned in a      ║
║     paragraph containing 3 hotels. Return a JSON array.        ║
║     Which technique handles arrays most reliably?              ║
║                                                                 ║
║  4. STRUCTURED OUTPUT PIPELINE                                  ║
║     Chain Lesson 3's agentic loop with this lesson:            ║
║     → User describes a city                                     ║
║     → Agent calls get_weather tool                             ║
║     → Results returned as validated JSON to the user           ║
╚══════════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    run()
    print(CHALLENGES)
