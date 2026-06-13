# Lesson 3: Agentic Loop - Running Notes
## Project: Day 2 - Agentic AI Prompt Engineering

## What This Lesson Does

This lesson demonstrates a **real multi-turn AI agent** using Gemini's native function calling API. The agent:
- Calls tools (weather, currency conversion, city info)
- Executes them in Python
- Feeds results back to the model
- Reasons over the results in a loop

## Prerequisites Completed

✅ Python packages installed  
✅ Virtual environment set up  
✅ API key configured in `.env`  
✅ Code fixes applied (API compatibility)  

## How to Run

### Option 1: Using Virtual Environment (Recommended)

```cmd
cd C:\Users\SRINATH\Downloads\Agentic_AI\Day2_Agentic_AI\Day2_PromptEngineering
venv\Scripts\activate
python intermediate\lesson_03_agentic_loop.py
```

### Option 2: Direct Command (Without Activating venv)

```cmd
cd C:\Users\SRINATH\Downloads\Agentic_AI\Day2_Agentic_AI\Day2_PromptEngineering
venv\Scripts\python.exe intermediate\lesson_03_agentic_loop.py
```

## What You'll See

The script runs 4 exercises automatically:

### Exercise 1: Single Tool Call
**Query:** "What's the weather like in Tokyo?"
- Agent calls `get_weather("Tokyo")`
- Returns: 28°C, Sunny, 55% humidity

### Exercise 2: Multiple Tool Calls (Comparison)
**Query:** "Is it warmer in London or Sydney right now?"
- Agent calls `get_weather("London")` → 14°C
- Agent calls `get_weather("Sydney")` → 18°C
- Compares and answers: Sydney is warmer

### Exercise 3: Two Different Tools
**Query:** "Convert 200 USD to Japanese Yen, and tell me the weather in Tokyo"
- Agent calls `convert_currency(200, "USD", "JPY")` → 31,480 JPY
- Agent calls `get_weather("Tokyo")` → 28°C, Sunny

### Exercise 4: Three Tools Chained
**Query:** "I'm visiting Paris. What's the local language, current weather, and how much is 50 USD in Euros?"
- Agent calls `get_city_info("Paris")` → French, GMT+2
- Agent calls `get_weather("Paris")` → 17°C, Clear
- Agent calls `convert_currency(50, "USD", "EUR")` → 46 EUR

## Key Concepts Demonstrated

1. **Tool Declaration** - Declaring function schemas to the Gemini API
2. **Function Dispatcher** - Mapping model calls to Python functions
3. **Agentic Loop** - Multi-turn conversation with tool execution
4. **Structured Response** - Model returns `FunctionCall` objects, not strings

## Technical Details

- **Model Used:** `gemini-flash-lite-latest` (better free tier quota)
- **API:** Google Generative AI SDK v0.8.6
- **Tools Available:** 
  - `get_weather(city, unit)` - Simulated weather data
  - `convert_currency(amount, from_curr, to_curr)` - Currency conversion
  - `get_city_info(city)` - City metadata (country, timezone, language)

## Fixes Applied

The original lesson code had compatibility issues. Here's what was fixed:

### 1. Package Upgrade
```cmd
pip install --upgrade google-generativeai
```
Upgraded from 0.7.2 → 0.8.6

### 2. Import Changes
**Before:**
```python
from google.generativeai import types
types.Schema(...)
```

**After:**
```python
from google.generativeai import protos
protos.Schema(...)
```

### 3. Environment Variables
Added `.env` file loading:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Model Selection
Changed from `gemini-1.5-flash` → `gemini-flash-lite-latest` to avoid quota issues

## Common Issues & Solutions

### Issue 1: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'google.generativeai'`

**Solution:** You're using system Python instead of venv Python
```cmd
venv\Scripts\python.exe intermediate\lesson_03_agentic_loop.py
```

### Issue 2: Quota Exceeded
**Error:** `429 You exceeded your current quota`

**Solution:** 
- Wait 1 minute for quota reset
- Or switch models (already using lite version)
- Or get a new API key from https://aistudio.google.com/apikey

### Issue 3: AttributeError Schema
**Error:** `AttributeError: module 'google.generativeai.types' has no attribute 'Schema'`

**Solution:** Already fixed - now using `protos.Schema` instead

## Coding Challenges (Optional)

Try these extensions after running the base lesson:

### Challenge 1: Add Flight Search Tool
Create `search_flights(from_city, to_city, date)` that returns hardcoded flight info and register it with the Gemini tool schema.

Test query: "Flights from London to Tokyo"

### Challenge 2: Add Turn Counter
Modify `agent_run()` to track and print how many tool calls each query required.

Expected output:
- Exercise 1: 1 tool call
- Exercise 2: 2 tool calls
- Exercise 3: 2 tool calls
- Exercise 4: 3 tool calls

### Challenge 3: Test Error Handling
Remove `"get_city_info"` from `TOOL_MAP` but keep it in `TOOL_DECLARATIONS`.

Question: What does the model do when the tool call errors?

## File Structure

```
Day2_PromptEngineering/
├── .env                              # Your API keys (DO NOT COMMIT)
├── requirements.txt                  # Python dependencies
├── venv/                            # Virtual environment
└── intermediate/
    └── lesson_03_agentic_loop.py    # The lesson script
```

## Additional Resources

- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs
- **Function Calling Guide:** https://ai.google.dev/gemini-api/docs/function-calling
- **Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits
- **Check Quota:** https://ai.dev/rate-limit

## Notes

- The deprecation warning about `google.generativeai` → `google.genai` is normal and can be ignored for now
- Tool responses are simulated (hardcoded data in dictionaries)
- The agent can chain up to 6 tool calls in a single conversation (safety limit)
- All weather/currency data is mock data for demonstration purposes

---

**Last Updated:** After successful run on June 13, 2026  
**Status:** ✅ Working - All 4 exercises completed successfully
