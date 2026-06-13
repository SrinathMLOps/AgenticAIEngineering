"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 3 — INTERMEDIATE: Build a Real Agentic Tool-Call Loop   ║
║  Topic: Multi-turn Agentic AI with Real Gemini Function Calling ║
╚══════════════════════════════════════════════════════════════════╝

You will implement a REAL function-calling agent using the
Gemini API's native tool-use feature — not prompt hacking.

This is how production agentic systems work:
  1. You declare tool schemas to the API
  2. The model returns a structured FunctionCall object
  3. You execute the function and feed the result back
  4. The model reasons over the result and responds

Run: python lesson_03_agentic_loop.py
Prereq: pip install google-generativeai
        $env:GEMINI_API_KEY = "your-key-here"
"""

import os, json
import google.generativeai as genai
from google.generativeai import types
from google.generativeai import protos
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────────────────────────
# STEP 1 ▶ Implement the Actual Tools (Python Functions)
# ─────────────────────────────────────────────────────────────────

WEATHER_DATA = {
    "london":    {"temp_c": 14, "condition": "Cloudy",  "humidity": 72},
    "tokyo":     {"temp_c": 28, "condition": "Sunny",   "humidity": 55},
    "new york":  {"temp_c": 22, "condition": "Partly Cloudy", "humidity": 61},
    "dubai":     {"temp_c": 41, "condition": "Very Hot","humidity": 30},
    "sydney":    {"temp_c": 18, "condition": "Rainy",   "humidity": 80},
    "berlin":    {"temp_c": 11, "condition": "Overcast","humidity": 68},
    "paris":     {"temp_c": 17, "condition": "Clear",   "humidity": 58},
}

EXCHANGE_RATES = {
    "usd_eur": 0.92, "usd_gbp": 0.79, "usd_jpy": 157.4, "usd_inr": 83.5,
    "eur_usd": 1.09, "gbp_usd": 1.27, "jpy_usd": 0.0064,"inr_usd": 0.012,
}

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Return simulated weather for a city."""
    data = WEATHER_DATA.get(city.lower().strip())
    if not data:
        return {"error": f"No weather data for '{city}'"}
    temp = data["temp_c"]
    if unit.lower() == "fahrenheit":
        temp = round(temp * 9/5 + 32, 1)
    return {
        "city": city.title(),
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%",
    }

def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
    """Convert a monetary amount between currencies."""
    key = f"{from_curr.lower()}_{to_curr.lower()}"
    rate = EXCHANGE_RATES.get(key)
    if not rate:
        return {"error": f"No rate for {from_curr}→{to_curr}"}
    converted = round(amount * rate, 2)
    return {
        "original":  f"{amount} {from_curr.upper()}",
        "converted": f"{converted} {to_curr.upper()}",
        "rate":       rate,
    }

def get_city_info(city: str) -> dict:
    """Return basic information about a city."""
    city_db = {
        "london":   {"country": "UK",      "timezone": "GMT+1",  "language": "English"},
        "tokyo":    {"country": "Japan",   "timezone": "GMT+9",  "language": "Japanese"},
        "new york": {"country": "USA",     "timezone": "GMT-4",  "language": "English"},
        "dubai":    {"country": "UAE",     "timezone": "GMT+4",  "language": "Arabic"},
        "sydney":   {"country": "Australia","timezone": "GMT+10","language": "English"},
        "berlin":   {"country": "Germany", "timezone": "GMT+2",  "language": "German"},
        "paris":    {"country": "France",  "timezone": "GMT+2",  "language": "French"},
    }
    info = city_db.get(city.lower().strip())
    if not info:
        return {"error": f"No info for '{city}'"}
    return {"city": city.title(), **info}

# ─────────────────────────────────────────────────────────────────
# STEP 2 ▶ Declare Tool Schemas for the Gemini API
# ─────────────────────────────────────────────────────────────────

TOOL_DECLARATIONS = [
    protos.Tool(function_declarations=[
        protos.FunctionDeclaration(
            name="get_weather",
            description="Get current weather for a city",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "city": protos.Schema(type=protos.Type.STRING, description="City name"),
                    "unit": protos.Schema(type=protos.Type.STRING,
                                        description="celsius or fahrenheit"),
                },
                required=["city"],
            ),
        ),
        protos.FunctionDeclaration(
            name="convert_currency",
            description="Convert an amount between two currencies",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "amount":    protos.Schema(type=protos.Type.NUMBER),
                    "from_curr": protos.Schema(type=protos.Type.STRING, description="e.g. USD"),
                    "to_curr":   protos.Schema(type=protos.Type.STRING, description="e.g. EUR"),
                },
                required=["amount", "from_curr", "to_curr"],
            ),
        ),
        protos.FunctionDeclaration(
            name="get_city_info",
            description="Get country, timezone and language for a city",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "city": protos.Schema(type=protos.Type.STRING),
                },
                required=["city"],
            ),
        ),
    ])
]

# ─────────────────────────────────────────────────────────────────
# STEP 3 ▶ Tool Dispatcher — Route model calls to Python functions
# ─────────────────────────────────────────────────────────────────

TOOL_MAP = {
    "get_weather":      get_weather,
    "convert_currency": convert_currency,
    "get_city_info":    get_city_info,
}

def dispatch(function_call) -> str:
    """Execute a Gemini FunctionCall and return JSON string result."""
    name   = function_call.name
    args   = dict(function_call.args)
    fn     = TOOL_MAP.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = fn(**args)
    return json.dumps(result, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────
# STEP 4 ▶ The Agentic Loop
# ─────────────────────────────────────────────────────────────────

def agent_run(user_query: str, model: genai.GenerativeModel, verbose: bool = True) -> str:
    """
    Core agentic loop:
      LOOP:
        1. Send messages to model
        2. If model calls a tool → execute → append result → continue
        3. If model returns text → done
    """
    history = [{"role": "user", "parts": [user_query]}]
    if verbose:
        print(f"\n  ┌─ USER: {user_query}")

    for turn in range(6):   # safety cap
        response = model.generate_content(history, tools=TOOL_DECLARATIONS)
        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        # ── Tool call branch ──
        if hasattr(part, "function_call") and part.function_call.name:
            fc     = part.function_call
            result = dispatch(fc)

            if verbose:
                print(f"  ├─ TOOL CALL [{turn+1}]: {fc.name}({dict(fc.args)})")
                print(f"  │  RESULT: {result}")

            # Append model's tool call + tool result to history
            history.append({"role": "model",  "parts": [part]})
            history.append({
                "role": "user",
                "parts": [protos.Part(
                    function_response=protos.FunctionResponse(
                        name=fc.name,
                        response={"result": json.loads(result)}
                    )
                )]
            })

        # ── Final text branch ──
        else:
            final_text = part.text.strip()
            if verbose:
                print(f"  └─ AGENT: {final_text}\n")
            return final_text

    return "[Max turns reached]"

# ─────────────────────────────────────────────────────────────────
# STEP 5 ▶ Run Exercises
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a helpful travel assistant with access to weather, "
    "currency, and city information tools. "
    "Always call the appropriate tool before answering."
)

EXERCISES = [
    # Exercise A — Single tool call
    "What's the weather like in Tokyo?",

    # Exercise B — Comparison requiring two calls
    "Is it warmer in London or Sydney right now?",

    # Exercise C — Two different tools chained
    "Convert 200 USD to Japanese Yen, and also tell me the weather in Tokyo.",

    # Exercise D — Three tools: city info + weather + currency
    "I'm visiting Paris. What's the local language, current weather, "
    "and how much is 50 USD in Euros?",
]

def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[!] Set GEMINI_API_KEY to run this lesson.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-flash-lite-latest",
        system_instruction=SYSTEM_PROMPT,
    )

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  LESSON 3: AGENTIC LOOP — Gemini Native Function Calling        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    for i, query in enumerate(EXERCISES, 1):
        print(f"\n{'━'*65}")
        print(f"  EXERCISE {i}")
        agent_run(query, model, verbose=True)

    print("""
╔══════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Add a new tool: search_flights(from, to, date) that     ║
║     returns hardcoded flight info and register it with the  ║
║     Gemini tool schema. Test: "Flights from London to Tokyo" ║
║                                                             ║
║  2. Add a turn counter to agent_run() and print how many    ║
║     tool calls each query required. Which exercise uses the ║
║     most? Why?                                              ║
║                                                             ║
║  3. Force a failure: remove "get_city_info" from TOOL_MAP   ║
║     but keep it in TOOL_DECLARATIONS. What does the model  ║
║     do when the tool call errors?                           ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    run()
