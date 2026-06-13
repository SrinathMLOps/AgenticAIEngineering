# Day 1 — Bare-Metal ReAct Agent

Three self-contained projects that each run out of the box. Start with `simple/`,
read the code, understand it, then move to `intermediate/` and `advanced/` to see
exactly what one new idea looks like in isolation.

---

## How the ReAct Loop Works

Every project uses the same core loop. Understanding this diagram is the whole point of Day 1.

```
┌─────────────────────────────────────────────────┐
│                   User Task                      │
└─────────────────────┬───────────────────────────┘
                      │
              ┌───────▼────────┐
              │    THINK        │  ← Claude reasons: what should I do next?
              │  (Claude API)   │     stop_reason == "end_turn"  → finished
              └───────┬────────┘     stop_reason == "tool_use"  → call a tool
                      │
              ┌───────▼────────┐
              │     ACT         │  ← dispatch(tool_name, tool_input)
              │  (tool call)    │     runs locally: search / calc / file / weather / wiki
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │    OBSERVE      │  ← tool result added to message history
              │  (tool_result)  │     model sees it on the next iteration
              └───────┬────────┘
                      │
               loop or finish?
                      │
              ┌───────▼────────┐
              │  FINAL ANSWER   │
              └────────────────┘
```

---

## Project Structure

```
day1/
├── simple/           ← Start here
├── intermediate/     ← Add streaming, retry, cost tracking
├── advanced/         ← Add planning, caching, automated eval
└── README.md         ← You are here
```

Each project folder is completely self-contained — it has its own `tools/`,
`agent/`, `memory/`, `utils/`, `main.py`, and `requirements.txt`. You can copy
any single folder somewhere else and it will run without modification.

---

## Setup (same for all three levels)

```bash
# 1. Enter the level you want to work on
cd simple          # or intermediate / advanced

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
# Edit .env → ANTHROPIC_API_KEY=sk-ant-...

# 5. Run
python main.py

# 6. (Optional) Launch the web dashboard (simple level only)
python dashboard.py
# Then open http://localhost:7860 in your browser
```

---

## 🎨 Visual Dashboard

The `simple/` level includes a beautiful web dashboard to visualize the agent's thinking process!

```bash
cd simple
python dashboard.py
```

Then open **http://localhost:7860** in your browser to see:
- Color-coded THINK/ACT/OBSERVE/FINISH phases
- Real-time step-by-step execution
- Token usage and cost tracking
- Beautiful, shareable interface

📖 See [DASHBOARD_GUIDE.md](./DASHBOARD_GUIDE.md) for complete documentation.

---

## Level 1 — Simple

**What you learn:** The complete ReAct loop and two new tool types.

**What's new vs the raw loop:**
- `get_weather` — current conditions + 7-day forecast for any city (Open-Meteo, free, no key)
- `wikipedia_search` — instant Wikipedia summary for any topic (Wikipedia-API package)
- `MAX_STEPS = 15` — enough headroom for multi-step research tasks

**Files to study (in order):**

| File | What it teaches |
|------|----------------|
| `tools/weather.py` | How to call a REST API and format the result for the model |
| `tools/wikipedia.py` | How to wrap a third-party Python library as a tool |
| `tools/registry.py` | How to register tools and dispatch calls by name |
| `agent/loop.py` | The core THINK → ACT → OBSERVE loop |
| `utils/logger.py` | How Rich panels make the loop readable in the terminal |

**Try these tasks:**
```
"What is the current weather in Tokyo? Give me a 3-day forecast."
"Who invented the World Wide Web? Look it up on Wikipedia and save the answer."
"Search the web for the 3 most popular languages in 2024, look each up on Wikipedia,
 save a ranked summary to languages.txt"
```

---

## Level 2 — Intermediate

**What you learn:** Making the agent production-ready — faster, cheaper, and fault-tolerant.

**What's new vs Simple (look for `# NEW` comments in the code):**

### 1. Streaming output (`agent/loop.py` → `_call_api`)
```python
# Before (Simple) — user sees nothing until the whole response arrives
response = client.messages.create(...)

# After (Intermediate) — tokens appear live as they generate
with client.messages.stream(**kwargs) as stream:
    for token in stream.text_stream:
        print(token, end="", flush=True)
    response = stream.get_final_message()   # same object, same loop logic
```
Toggle with `STREAM_OUTPUT=false` in your `.env` to compare.

### 2. Retry on tool error (`agent/loop.py` → `_dispatch_with_retry`)
```python
# Before (Simple) — one attempt, error returned to model immediately
result, is_error = dispatch(tool_name, tool_input)

# After (Intermediate) — retry up to MAX_RETRIES times on transient failures
for attempt in range(1, MAX_RETRIES + 1):
    result, is_error = dispatch(tool_name, tool_input)
    if not is_error:
        break
```
Set `MAX_RETRIES=0` to disable and see flaky network errors come back.

### 3. Token usage tracker (`agent/loop.py` + `utils/logger.py`)
```python
# Every API response contains usage counts — just accumulate them
total_input_tokens  += response.usage.input_tokens
total_output_tokens += response.usage.output_tokens

# Print cost at the end
log_token_usage(total_input_tokens, total_output_tokens)
```
Run a simple task and a complex research task — compare the cost difference.

**Try these tasks:**
```
"Explain how HTTPS works, step by step."         # watch tokens stream live
"Search for Python web frameworks — top 5."      # see retry recover a hiccup
"Look up the history of the internet and save a summary."  # read the token cost
```

---

## Level 3 — Advanced

**What you learn:** Planning, caching, and automated evaluation.

**What's new vs Intermediate (look for `# NEW` comments):**

### 1. Plan-first step (`agent/loop.py` → `_plan_phase`)
```python
# Before the ReAct loop, ask the model to write its plan
response = client.messages.create(
    messages=[{"role": "user", "content": f"Task: {task}\n\n{_PLAN_PROMPT}"}],
)
plan = extract_text(response.content)
log_plan(plan)          # shows the 📋 PLAN panel

# Inject the plan into the task so the loop follows it
task = f"{task}\n\n[Your plan]\n{plan}\n\nNow execute your plan step by step."
```
Try setting `PLAN_FIRST=false` to see how much less structured the output is.

### 2. Tool result caching (`tools/registry.py`)
```python
cache_key = f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}"

if tool_name not in _NO_CACHE and cache_key in _cache:
    return f"[cached] {_cache[cache_key]}", False   # instant, no network call

result = str(run_fn(**tool_input))
_cache[cache_key] = result                           # store for next time
```
Give the agent a task that involves verifying the same Wikipedia article twice —
the second call will show `[cached]` in the OBSERVE panel and complete instantly.

### 3. Eval harness (`eval_harness.py`)
```
python eval_harness.py
```
Runs 5 deterministic tasks, scores each pass/fail, prints accuracy, and saves
`eval_results.json`. This is the pattern used in real agent evaluation pipelines:
fixed tasks + automated check functions + logged results.

**Try these tasks:**
```
"Research the history of AI: milestones, key people, current state. Save a report."
"Compare Python and JavaScript — Wikipedia + popularity search + save a table."
python eval_harness.py    # run the full benchmark
```

---

## What Each File Does (Quick Reference)

```
<level>/
├── main.py               Entry point. Loads .env, calls runner.
├── requirements.txt      pip dependencies for this level.
├── .env.example          Copy to .env and add your API key.
│
├── agent/
│   ├── loop.py           ★ Core ReAct loop — the main thing to read
│   └── runner.py         Interactive menu + example tasks
│
├── memory/
│   └── buffer.py         Stores message history (user / assistant / tool_result)
│
├── tools/
│   ├── registry.py       Registers all tools; dispatches calls by name
│   ├── calculator.py     Safe AST-based Python expression evaluator
│   ├── file_io.py        Read/write files (path-traversal safe)
│   ├── search.py         DuckDuckGo web search (no key needed)
│   ├── weather.py        Open-Meteo weather + forecast (no key needed)  ← Simple+
│   └── wikipedia.py      Wikipedia article summary  ← Simple+
│
└── utils/
    ├── logger.py         Coloured Rich panels: THINK / ACT / OBSERVE / FINISH
    │                     + TOKEN USAGE panel (Intermediate+)
    │                     + PLAN panel (Advanced)
    └── schema.py         Pydantic model for ToolCall
```

---

## Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `ANTHROPIC_API_KEY` | — | **Required.** Your Anthropic key. |
| `MODEL` | `claude-sonnet-4-20250514` | Any Anthropic model name. |
| `MAX_STEPS` | `15` | Hard stop after this many loop iterations. |
| `MAX_RETRIES` | `2` | Extra attempts on tool error (Intermediate+). |
| `STREAM_OUTPUT` | `true` | Live token streaming (Intermediate+). |
| `PLAN_FIRST` | `true` | Force a plan before acting (Advanced). |
#   A g e n t i c A I E n g i n e e r i n g 
 
 