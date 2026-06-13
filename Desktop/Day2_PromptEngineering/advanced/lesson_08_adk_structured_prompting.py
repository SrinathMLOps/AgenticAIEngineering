"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 8 — STRUCTURED PROMPTING WITH GOOGLE ADK                ║
║  Topic: Agent Development Kit · Typed Agents · Structured Output ║
╚══════════════════════════════════════════════════════════════════╝

Google ADK (Agent Development Kit) is Google's official framework
for building production-grade agentic AI systems. Unlike raw API
calls, ADK gives you:

  • Declarative agent definitions (name, instruction, model, tools)
  • Native Pydantic output_schema → guaranteed typed responses
  • InMemoryRunner for local testing
  • Sequential / Parallel agent orchestration
  • Built-in tool calling lifecycle

This lesson teaches STRUCTURED PROMPTING through ADK:
  The instruction IS your structured prompt — it's the system prompt
  written in ADK's modular, reusable agent format.

PARTS:
  Part 1 — Environment setup + first ADK agent
  Part 2 — Structured output with Pydantic schemas
  Part 3 — Tool-equipped agents with structured results
  Part 4 — Sequential agents: Extractor → Formatter → Validator
  Part 5 — Prompt variant comparison (the 5 techniques, ADK-style)

Run: python lesson_08_adk_structured_prompting.py
Prereq:
  pip install google-adk pydantic python-dotenv
  Copy .env.template to .env and fill in GEMINI_API_KEY
"""

import asyncio
import json
import os
from typing import Optional

# ── Load .env if present ────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; can use $env: instead

# ── Validate env early ──────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("╔══════════════════════════════════════════════════════╗")
    print("║  [!] GEMINI_API_KEY not set.                        ║")
    print("║  Set it in .env or run:                             ║")
    print("║  $env:GEMINI_API_KEY = 'your-key'  (PowerShell)    ║")
    print("╚══════════════════════════════════════════════════════╝")
    exit(1)

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")

# ── ADK imports ─────────────────────────────────────────────────
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from pydantic import BaseModel, Field

MODEL = os.environ.get("DEFAULT_GEMINI_MODEL", "gemini-2.0-flash")

# ─────────────────────────────────────────────────────────────────
# HELPER: Run an agent with InMemoryRunner and print results
# ─────────────────────────────────────────────────────────────────

async def run_agent(agent: LlmAgent, user_message: str, label: str = "") -> str:
    """
    Runs an ADK LlmAgent using InMemoryRunner.
    Returns the final text response.
    """
    session_service = InMemorySessionService()
    runner = InMemoryRunner(agent=agent, session_service=session_service)
    session = await session_service.create_session(
        app_name=agent.name, user_id="student_01"
    )

    final_text = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_message
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text += part.text

    if label:
        print(f"\n  [{label}]")
        print(f"  Input : {user_message[:80]}")
        print(f"  Output: {final_text.strip()[:300]}")
    return final_text.strip()


# ═════════════════════════════════════════════════════════════════
# PART 1 ▶ First ADK Agent — The Instruction IS the Structured Prompt
# ═════════════════════════════════════════════════════════════════
# In ADK, the `instruction` parameter replaces the system prompt.
# Think of it as a named, versioned, reusable system prompt.
#
# Structured prompting rule: the instruction defines:
#   1. ROLE  — what the agent is
#   2. TASK  — what it must do
#   3. FORMAT— exactly how to output it

async def part1_first_agent():
    print("\n" + "═" * 65)
    print("  PART 1: First ADK Agent — Instruction as Structured Prompt")
    print("═" * 65)

    # ── Bad instruction (barebones / unstructured) ──────────────
    vague_agent = LlmAgent(
        name="vague_agent",
        model=MODEL,
        instruction="You are a helpful assistant.",
    )

    # ── Good instruction (fully structured) ─────────────────────
    structured_agent = LlmAgent(
        name="structured_agent",
        model=MODEL,
        instruction=(
            "You are a weather information extractor.\n\n"
            "TASK: When given a city name, output ONLY a JSON object with:\n"
            "  - city: the city name (string)\n"
            "  - country: the country name (string)\n"
            "  - description: one sentence about the city's typical climate (string)\n\n"
            "FORMAT RULE: Output ONLY the JSON. No markdown, no prose."
        ),
    )

    query = "Tell me about the weather in Tokyo."
    await run_agent(vague_agent,     query, label="VAGUE instruction")
    await run_agent(structured_agent, query, label="STRUCTURED instruction")

    print("""
  KEY INSIGHT:
  The 'instruction' is your structured prompt. ADK stores it as
  a named, reusable artifact — unlike ad-hoc system_instruction
  strings, ADK agents can be versioned, tested, and swapped.
""")


# ═════════════════════════════════════════════════════════════════
# PART 2 ▶ Pydantic output_schema — Typed, Validated JSON Output
# ═════════════════════════════════════════════════════════════════
# ADK's output_schema enforces the response structure at the
# DECODING level — not just via prompting. The model is constrained
# to only produce tokens that match the Pydantic schema.

class WeatherReport(BaseModel):
    city:        str   = Field(description="Name of the city")
    country:     str   = Field(description="Country the city is in")
    climate:     str   = Field(description="General climate type e.g. 'humid subtropical'")
    avg_summer_c: float = Field(description="Average summer temperature in Celsius")
    avg_winter_c: float = Field(description="Average winter temperature in Celsius")
    rainy_season: bool  = Field(description="Whether the city has a distinct rainy season")

class TravelTip(BaseModel):
    city:     str        = Field(description="City name")
    tips:     list[str]  = Field(description="3-5 practical travel tips for the city")
    best_months: list[str] = Field(description="Best months to visit e.g. ['March', 'April']")

async def part2_typed_output():
    print("\n" + "═" * 65)
    print("  PART 2: Pydantic output_schema — Guaranteed Typed Output")
    print("═" * 65)

    # ── Agent with typed output ──────────────────────────────────
    weather_agent = LlmAgent(
        name="weather_schema_agent",
        model=MODEL,
        instruction=(
            "You are a climate expert. Given a city name, provide accurate "
            "climate information. Use real-world knowledge — your output will "
            "be validated against a strict schema."
        ),
        output_schema=WeatherReport,    # ← ADK enforces this schema
        output_key="weather_data",      # ← stores result in session state
    )

    travel_agent = LlmAgent(
        name="travel_tip_agent",
        model=MODEL,
        instruction=(
            "You are a travel advisor. Given a city, provide practical, "
            "specific travel tips based on local culture and climate."
        ),
        output_schema=TravelTip,
        output_key="travel_data",
    )

    cities = ["Tokyo", "Nairobi", "Buenos Aires"]
    for city in cities:
        print(f"\n  City: {city}")
        print(f"  {'─'*50}")

        raw = await run_agent(weather_agent, city)
        try:
            data = WeatherReport.model_validate_json(raw)
            print(f"  Climate   : {data.climate}")
            print(f"  Summer avg: {data.avg_summer_c}°C  |  Winter avg: {data.avg_winter_c}°C")
            print(f"  Rainy season: {'Yes' if data.rainy_season else 'No'}")
        except Exception as e:
            print(f"  (Schema validation note: {e})")
            print(f"  Raw: {raw[:200]}")

    print("""
  KEY INSIGHT:
  output_schema uses Pydantic's JSON mode under the hood —
  the same mechanism as response_mime_type='application/json'
  but with field-level validation and type coercion built in.
  You get structured output without writing extraction regex.
""")


# ═════════════════════════════════════════════════════════════════
# PART 3 ▶ Tool-Equipped Agent with Structured Output
# ═════════════════════════════════════════════════════════════════

# Real tool functions — ADK discovers them via function signature
CITY_DB = {
    "tokyo":       {"timezone": "JST (UTC+9)", "currency": "JPY", "language": "Japanese"},
    "nairobi":     {"timezone": "EAT (UTC+3)", "currency": "KES", "language": "Swahili/English"},
    "london":      {"timezone": "BST (UTC+1)", "currency": "GBP", "language": "English"},
    "dubai":       {"timezone": "GST (UTC+4)", "currency": "AED", "language": "Arabic"},
    "sydney":      {"timezone": "AEST (UTC+10)","currency": "AUD", "language": "English"},
    "paris":       {"timezone": "CEST (UTC+2)","currency": "EUR", "language": "French"},
}

def get_city_details(city: str) -> dict:
    """
    Retrieve timezone, currency and official language for a city.

    Args:
        city: The name of the city to look up.

    Returns:
        A dict with timezone, currency, and language keys.
    """
    data = CITY_DB.get(city.lower().strip())
    if not data:
        return {"error": f"No data found for city: {city}"}
    return {"city": city.title(), **data}

def get_visa_info(nationality: str, destination: str) -> dict:
    """
    Check simplified visa requirements for a traveller.

    Args:
        nationality: The traveller's nationality e.g. 'Indian'.
        destination: The destination country e.g. 'Japan'.

    Returns:
        A dict with visa_required (bool) and notes (str).
    """
    # Simplified lookup for demo
    free_visa = {
        ("british", "france"), ("american", "france"), ("german", "japan"),
        ("australian", "japan"), ("indian", "dubai"),
    }
    key = (nationality.lower(), destination.lower())
    required = key not in free_visa
    return {
        "nationality":  nationality,
        "destination":  destination,
        "visa_required": required,
        "notes": "Visa-free entry" if not required else "Visa required — check embassy"
    }

class TripPlan(BaseModel):
    city:          str       = Field(description="Destination city")
    timezone:      str       = Field(description="Local timezone")
    currency:      str       = Field(description="Local currency code")
    language:      str       = Field(description="Primary language spoken")
    visa_required: bool      = Field(description="Whether a visa is required")
    visa_note:     str       = Field(description="Brief visa guidance")
    packing_tips:  list[str] = Field(description="3 packing tips specific to this destination")

async def part3_tool_agent():
    print("\n" + "═" * 65)
    print("  PART 3: Tool-Equipped Agent + Structured Output")
    print("═" * 65)

    trip_planner = LlmAgent(
        name="trip_planner_agent",
        model=MODEL,
        instruction=(
            "You are a travel planning assistant.\n\n"
            "When a user provides their nationality and destination city:\n"
            "1. Call get_city_details to retrieve city info.\n"
            "2. Call get_visa_info to check visa requirements.\n"
            "3. Combine the results and add 3 specific packing tips.\n"
            "4. Return the complete structured plan."
        ),
        tools=[get_city_details, get_visa_info],
        output_schema=TripPlan,
    )

    queries = [
        "I am Indian and I want to visit Dubai.",
        "I am British and planning to visit Paris.",
    ]

    for query in queries:
        print(f"\n  Query: {query}")
        raw = await run_agent(trip_planner, query)
        try:
            plan = TripPlan.model_validate_json(raw)
            print(f"  City      : {plan.city} ({plan.timezone})")
            print(f"  Currency  : {plan.currency}  |  Language: {plan.language}")
            print(f"  Visa      : {'Required' if plan.visa_required else 'Not required'}  — {plan.visa_note}")
            print(f"  Packing   : {', '.join(plan.packing_tips[:2])}...")
        except Exception as e:
            print(f"  Raw: {raw[:300]}")

    print("""
  KEY INSIGHT:
  ADK's tool calling lifecycle:
    1. Model sees instruction + tool schemas (auto-generated from docstrings)
    2. Model emits FunctionCall → ADK dispatches to your Python function
    3. ADK appends FunctionResponse to context
    4. Model reads result and fills the output_schema
  You never write the dispatch loop — ADK handles it.
""")


# ═════════════════════════════════════════════════════════════════
# PART 4 ▶ Sequential Agent Pipeline (Prompt Chaining Pattern)
# ═════════════════════════════════════════════════════════════════
# Each agent has a highly focused instruction = structured prompt.
# Sequential pipeline: Extractor → Formatter → Scorer

class ExtractedData(BaseModel):
    topic:      str       = Field(description="Main subject of the text")
    key_points: list[str] = Field(description="3-5 key facts extracted")
    sentiment:  str       = Field(description="positive, negative, or neutral")
    word_count: int       = Field(description="Approximate word count of input text")

class FormattedReport(BaseModel):
    title:      str       = Field(description="Short report title")
    summary:    str       = Field(description="2-sentence summary")
    bullets:    list[str] = Field(description="Bullet points for a slide")
    action_item: str      = Field(description="One recommended follow-up action")

async def part4_sequential():
    print("\n" + "═" * 65)
    print("  PART 4: Sequential Agent Pipeline — Prompt Chaining")
    print("═" * 65)

    # Stage 1: Extract structured data from raw text
    extractor = LlmAgent(
        name="extractor_agent",
        model=MODEL,
        instruction=(
            "You are a data extraction specialist.\n"
            "Extract: topic, key_points (list of 3-5), sentiment, and "
            "approximate word count from the provided text.\n"
            "Be precise and factual — do not infer beyond what is stated."
        ),
        output_schema=ExtractedData,
    )

    # Stage 2: Format the extracted data into a report
    formatter = LlmAgent(
        name="formatter_agent",
        model=MODEL,
        instruction=(
            "You are a professional report writer.\n"
            "Given extracted data, create a formatted report with:\n"
            "  - A concise title\n"
            "  - A 2-sentence executive summary\n"
            "  - 3-4 bullet points suitable for a presentation slide\n"
            "  - One recommended action item\n"
            "Keep all content professional and concise."
        ),
        output_schema=FormattedReport,
    )

    # Sample text to process
    sample_text = """
    The global electric vehicle (EV) market grew by 35% in 2024, driven primarily
    by aggressive price reductions from Chinese manufacturers. Battery costs have
    fallen below $100 per kWh for the first time, a milestone analysts previously
    predicted for 2026. However, charging infrastructure remains a critical
    bottleneck in rural regions, with only 1 public charger per 42 EVs in some
    markets. European automakers have responded by committing an additional $180bn
    in EV investment over the next five years, signaling a major industry shift.
    """.strip()

    print(f"\n  Input text: {sample_text[:100]}...\n")

    # Stage 1: Extract
    print("  [Stage 1 — Extractor Agent]")
    raw_extracted = await run_agent(extractor, sample_text)
    try:
        extracted = ExtractedData.model_validate_json(raw_extracted)
        print(f"  Topic     : {extracted.topic}")
        print(f"  Sentiment : {extracted.sentiment}")
        print(f"  Key points: {len(extracted.key_points)} found")
        for kp in extracted.key_points:
            print(f"    • {kp}")

        # Stage 2: Format using the extracted data as input
        print("\n  [Stage 2 — Formatter Agent]")
        formatter_input = (
            f"Topic: {extracted.topic}\n"
            f"Key points: {'; '.join(extracted.key_points)}\n"
            f"Sentiment: {extracted.sentiment}"
        )
        raw_report = await run_agent(formatter, formatter_input)
        try:
            report = FormattedReport.model_validate_json(raw_report)
            print(f"  Title      : {report.title}")
            print(f"  Summary    : {report.summary}")
            print(f"  Bullets    : {len(report.bullets)} slide points")
            print(f"  Action     : {report.action_item}")
        except Exception as e:
            print(f"  Formatter raw: {raw_report[:300]}")
    except Exception as e:
        print(f"  Extractor note: {e}\n  Raw: {raw_extracted[:300]}")

    print("""
  KEY INSIGHT:
  Each agent in the pipeline has ONE job, defined by a focused
  instruction. This is modular structured prompting — no single
  prompt tries to extract AND format AND score. Split the work,
  keep each instruction tight, and compose the results.
""")


# ═════════════════════════════════════════════════════════════════
# PART 5 ▶ Comparing the 5 Prompt Structures — ADK Style
# ═════════════════════════════════════════════════════════════════

async def part5_variant_comparison():
    print("\n" + "═" * 65)
    print("  PART 5: 5 Instruction Variants Compared (ADK Agent Each)")
    print("═" * 65)

    class ExtractionResult(BaseModel):
        hotel:   str   = Field(description="Hotel name")
        city:    str   = Field(description="City name")
        rating:  float = Field(description="Overall rating out of 5")
        recommend: bool = Field(description="Would the reviewer recommend it")

    review = (
        "We spent 4 nights at The Majestic Grand in Vienna last August. "
        "The breakfast was world-class (5/5) but the WiFi was terrible (1/5). "
        "Overall: 3.5/5. Despite the WiFi issues, I would recommend it for the location."
    )

    variants = {
        "A_Barebones": "Extract hotel info from the review.",

        "B_SchemaHint": (
            "Extract hotel information from the review.\n"
            "Required fields: hotel (string), city (string), "
            "rating (float 0-5), recommend (boolean).\n"
            "Output ONLY valid JSON."
        ),

        "C_OneShot": (
            "Extract hotel information from reviews.\n\n"
            "Example:\n"
            'Input: "2 nights at Hotel Blue in Rome. Great food (4/5). Overall 4/5. Would return."\n'
            'Output: {"hotel":"Hotel Blue","city":"Rome","rating":4.0,"recommend":true}\n\n'
            "Now extract from the given review. Output ONLY JSON:"
        ),

        "D_CoT": (
            "Extract hotel information step by step:\n"
            "Step 1: Find the hotel name.\n"
            "Step 2: Find the city.\n"
            "Step 3: Find the overall rating (float).\n"
            "Step 4: Determine if reviewer recommends it (true/false).\n"
            "Step 5: Output ONLY the JSON with keys: hotel, city, rating, recommend."
        ),

        "E_Constrained": (
            "Extract hotel data from the review.\n"
            "Required: hotel, city, rating (float), recommend (bool).\n"
            "Complete the following JSON exactly:\n{"
        ),
    }

    results = {}
    for name, instruction in variants.items():
        agent = LlmAgent(
            name=f"variant_{name.lower()}",
            model=MODEL,
            instruction=instruction,
            output_schema=ExtractionResult,
        )
        raw = await run_agent(agent, review)
        try:
            data = ExtractionResult.model_validate_json(raw)
            score = 100  # schema enforced by ADK
            results[name] = ("✅", score, data)
            print(f"  {name:<22}  ✅  hotel={data.hotel}, city={data.city}, rating={data.rating}")
        except Exception:
            # Try manual extraction if schema validation fails
            results[name] = ("⚠️ ", 30, None)
            print(f"  {name:<22}  ⚠️   Schema validation failed — raw: {raw[:80]}")

    print(f"""
  NOTE: With output_schema, ADK uses constrained decoding —
  all 5 variants should produce valid JSON. The DIFFERENCE
  becomes visible without output_schema (see Lesson 2 for that).
  Here, the key learning is HOW INSTRUCTION QUALITY affects
  the ACCURACY of field values, not just whether JSON is valid.
""")


# ═════════════════════════════════════════════════════════════════
# MAIN — Run all parts
# ═════════════════════════════════════════════════════════════════

async def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  LESSON 8: STRUCTURED PROMPTING WITH GOOGLE ADK                 ║")
    print("║  Model:", MODEL.ljust(55), "║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    await part1_first_agent()
    await part2_typed_output()
    await part3_tool_agent()
    await part4_sequential()
    await part5_variant_comparison()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                              ║
╠══════════════════════════════════════════════════════════════════╣
║  1. PARALLEL AGENTS                                             ║
║     Create a ParallelAgent that runs weather_agent and          ║
║     travel_tip_agent at the same time for the same city.        ║
║     Merge results into a single CityBrief Pydantic model.       ║
║                                                                 ║
║  2. MULTI-SCHEMA PIPELINE                                       ║
║     Extend Part 4 with a Stage 3 Scorer agent:                  ║
║     input = FormattedReport → output = ScoreCard(clarity: int,  ║
║     completeness: int, actionability: int, total: int)          ║
║                                                                 ║
║  3. CUSTOM TOOL + ADK                                           ║
║     Add a search_flights(from_city, to_city, date) tool to      ║
║     the trip_planner agent (Part 3). Return a FlightOption      ║
║     Pydantic model with airline, price_usd, duration_hrs.       ║
║                                                                 ║
║  4. ADK WEB UI                                                  ║
║     Run: adk web                                               ║
║     Open http://localhost:8000 and test your agents visually.   ║
║     Inspect the full tool-calling trace in the browser.         ║
╚══════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    asyncio.run(main())
