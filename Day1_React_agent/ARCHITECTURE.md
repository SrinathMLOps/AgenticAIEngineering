# 🏗️ Architecture & Visual Guide

This document provides visual diagrams to help you understand the system architecture.

---

## 🎯 The ReAct Loop (Conceptual)

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER GIVES TASK                            │
│               "What's the weather in Tokyo?"                      │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ Initialize
                                ▼
                    ┌───────────────────────┐
                    │  Conversation Memory   │
                    │  [user task]           │
                    └───────────────────────┘
                                │
                                │
╔═══════════════════════════════▼═══════════════════════════════════╗
║                         REACT LOOP                                 ║
║                     (Repeat until done)                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌────────────────────────────────────────────────────────────┐  ║
║  │ 🤔 THINK (Call Claude API)                                 │  ║
║  │                                                            │  ║
║  │ Input: System prompt + Tools + Memory                      │  ║
║  │ Output: Reasoning + Decision                               │  ║
║  │                                                            │  ║
║  │ Claude decides:                                            │  ║
║  │   • "I need to call a tool" → tool_use                     │  ║
║  │   • "I'm done" → end_turn                                  │  ║
║  └──────────────────┬───────────────────┬─────────────────────┘  ║
║                     │                   │                         ║
║                     │                   │                         ║
║         stop_reason = tool_use      stop_reason = end_turn       ║
║                     │                   │                         ║
║                     ▼                   ▼                         ║
║  ┌────────────────────────────┐  ┌──────────────────────────┐   ║
║  │ 🔧 ACT (Run Tool)          │  │ ✅ FINISH                │   ║
║  │                            │  │                          │   ║
║  │ • Extract tool call        │  │ • Extract final answer   │   ║
║  │ • Dispatch to function     │  │ • Return to user         │   ║
║  │ • Get result               │  │ • DONE!                  │   ║
║  └──────────────┬─────────────┘  └──────────────────────────┘   ║
║                 │                           ▲                     ║
║                 ▼                           │                     ║
║  ┌────────────────────────────┐            │                     ║
║  │ 👁️ OBSERVE (Save Result)  │            │                     ║
║  │                            │            │                     ║
║  │ • Add tool result to       │            │                     ║
║  │   conversation memory      │            │                     ║
║  │ • Claude will see this     │            │                     ║
║  │   on next iteration        │            │                     ║
║  └──────────────┬─────────────┘            │                     ║
║                 │                           │                     ║
║                 └───────────────────────────┘                     ║
║                      Loop back to THINK                           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 📂 Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                      (Entry Point)                               │
│                                                                  │
│  • Load .env                                                     │
│  • Parse command-line args                                       │
│  • Call runner                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    agent/runner.py                               │
│                   (User Interface)                               │
│                                                                  │
│  • Show interactive menu                                         │
│  • Get user's task                                               │
│  • Call run_agent()                                              │
│  • Display results                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    agent/loop.py                                 │
│                  (ReAct Loop Core) ⭐                            │
│                                                                  │
│  • Initialize client, memory, tools                              │
│  • THINK: Call Claude API                                        │
│  • ACT: Dispatch tool calls                                      │
│  • OBSERVE: Save results                                         │
│  • FINISH: Return final answer                                   │
└──────────┬────────────────────────────────────┬─────────────────┘
           │                                    │
           │                                    │
           ▼                                    ▼
┌──────────────────────────┐      ┌──────────────────────────────┐
│   memory/buffer.py       │      │   tools/registry.py          │
│  (Conversation Memory)   │      │   (Tool Dispatcher)          │
│                          │      │                              │
│  • Store messages        │      │  • Register all tools        │
│  • Format for API        │      │  • Dispatch by name          │
│  • Track history         │      │  • Handle errors             │
└──────────────────────────┘      └──────────┬───────────────────┘
                                              │
                                              │
                       ┌──────────────────────┼──────────────────────┐
                       │                      │                      │
                       ▼                      ▼                      ▼
            ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
            │ tools/          │   │ tools/          │   │ tools/          │
            │ calculator.py   │   │ weather.py      │   │ wikipedia.py    │
            │                 │   │                 │   │                 │
            │ • Math eval     │   │ • Call API      │   │ • Search wiki   │
            │ • AST parsing   │   │ • Format result │   │ • Return summary│
            └─────────────────┘   └─────────────────┘   └─────────────────┘
                       │                      │                      │
                       └──────────────────────┴──────────────────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │  utils/logger.py    │
                                   │  (Pretty Output)    │
                                   │                     │
                                   │  • Color panels     │
                                   │  • Formatting       │
                                   └─────────────────────┘
```

---


## 💾 Memory Flow Diagram

```
STEP 1: User asks question
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory State:
┌─────────────────────────────────────────────────────┐
│ [                                                   │
│   {                                                 │
│     "role": "user",                                 │
│     "content": "What's the weather in Tokyo?"       │
│   }                                                 │
│ ]                                                   │
└─────────────────────────────────────────────────────┘


STEP 2: Claude responds with tool call
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory State:
┌─────────────────────────────────────────────────────┐
│ [                                                   │
│   { "role": "user", "content": "..." },            │
│   {                                                 │
│     "role": "assistant",                            │
│     "content": [                                    │
│       {                                             │
│         "type": "text",                             │
│         "text": "I'll check Tokyo's weather"        │
│       },                                            │
│       {                                             │
│         "type": "tool_use",                         │
│         "id": "toolu_123",                          │
│         "name": "get_weather",                      │
│         "input": {"city": "Tokyo"}                  │
│       }                                             │
│     ]                                               │
│   }                                                 │
│ ]                                                   │
└─────────────────────────────────────────────────────┘


STEP 3: Tool result added
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory State:
┌─────────────────────────────────────────────────────┐
│ [                                                   │
│   { "role": "user", "content": "..." },            │
│   { "role": "assistant", "content": [...] },       │
│   {                                                 │
│     "role": "user",    ← Tool results are "user"   │
│     "content": [                                    │
│       {                                             │
│         "type": "tool_result",                      │
│         "tool_use_id": "toolu_123",                 │
│         "content": "Tokyo: 15°C, Cloudy",           │
│         "is_error": false                           │
│       }                                             │
│     ]                                               │
│   }                                                 │
│ ]                                                   │
└─────────────────────────────────────────────────────┘


STEP 4: Claude's final response
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory State:
┌─────────────────────────────────────────────────────┐
│ [                                                   │
│   { "role": "user", "content": "..." },            │
│   { "role": "assistant", "content": [...] },       │
│   { "role": "user", "content": [...] },            │
│   {                                                 │
│     "role": "assistant",                            │
│     "content": "The weather in Tokyo is 15°C..."    │
│   }                                                 │
│ ]                                                   │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Tool Registration & Dispatch Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    tools/registry.py                             │
└─────────────────────────────────────────────────────────────────┘

TOOL_FUNCTIONS = {
    "calculator": calculate,          ←─────┐
    "get_weather": get_weather,       ←───┐ │
    "wikipedia_search": wiki_search,  ←─┐ │ │
    "web_search": web_search,         ← │ │ │
    "file_io": file_io                ← │ │ │
}                                       │ │ │
                                        │ │ │
TOOL_DEFINITIONS = [                   │ │ │
    {                                   │ │ │
        "name": "get_weather",          │ │ │
        "description": "...",           │ │ │
        "input_schema": {...}           │ │ │
    },                                  │ │ │
    ...                                 │ │ │
]                                       │ │ │
        │                               │ │ │
        │ get_tool_definitions()        │ │ │
        ▼                               │ │ │
┌─────────────────────────┐            │ │ │
│   Sent to Claude API    │            │ │ │
│   (Claude sees these    │            │ │ │
│    tool definitions)    │            │ │ │
└─────────────────────────┘            │ │ │
                                        │ │ │
                                        │ │ │
When Claude calls a tool:              │ │ │
                                        │ │ │
dispatch("get_weather", {"city": "Tokyo"})
        │                               │ │ │
        │ 1. Look up in TOOL_FUNCTIONS │ │ │
        └────────────────────────────────┘ │ │
                                          │ │
        │ 2. Get the function             │ │
        └────────────────────────────────────┘ │
                                            │
        │ 3. Call with parameters           │
        └────────────────────────────────────────┘
                │
                ▼
        ┌──────────────────┐
        │  get_weather()   │
        │  from weather.py │
        └────────┬─────────┘
                │
                ▼
        ┌──────────────────────────────┐
        │ 1. Geocode city → lat/lon    │
        │ 2. Call Open-Meteo API       │
        │ 3. Format result string      │
        └────────┬─────────────────────┘
                │
                ▼
        "Tokyo: 15°C, Cloudy..."
                │
                ▼
        ┌──────────────────┐
        │  Return result   │
        │  to agent/loop   │
        └──────────────────┘
```

---

## 🌊 Data Flow: Complete Example

```
USER INPUT
    │
    │ "What's the weather in Tokyo and save it?"
    │
    ▼
┌─────────────────────────────────────────────────┐
│              agent/loop.py                      │
│  memory.add_user("What's the weather...")       │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 1: THINK                       │
│  client.messages.create(                        │
│    messages=memory.get_messages(),              │
│    tools=get_tool_definitions()                 │
│  )                                              │
└────────────────────┬────────────────────────────┘
                     │
                     │ Response:
                     │ stop_reason = "tool_use"
                     │ tool_call = get_weather(city="Tokyo")
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 1: ACT                         │
│  dispatch("get_weather", {"city": "Tokyo"})     │
│    ├→ tools/registry.py                         │
│    └→ tools/weather.py                          │
│         ├→ Geocode API call                     │
│         └→ Weather API call                     │
│  Result: "Tokyo: 15°C, Cloudy..."               │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 1: OBSERVE                     │
│  memory.add_tool_result(                        │
│    tool_use_id="toolu_123",                     │
│    result="Tokyo: 15°C...",                     │
│    is_error=False                               │
│  )                                              │
└────────────────────┬────────────────────────────┘
                     │
                     │ Loop back
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 2: THINK                       │
│  client.messages.create(                        │
│    messages=memory.get_messages()  ← Now has    │
│                                      tool result │
│  )                                              │
└────────────────────┬────────────────────────────┘
                     │
                     │ Response:
                     │ stop_reason = "tool_use"
                     │ tool_call = file_io(
                     │   action="write",
                     │   path="tokyo.txt",
                     │   content="Tokyo: 15°C..."
                     │ )
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 2: ACT                         │
│  dispatch("file_io", {...})                     │
│    ├→ tools/registry.py                         │
│    └→ tools/file_io.py                          │
│         └→ Write file to disk                   │
│  Result: "Successfully wrote to tokyo.txt"      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 2: OBSERVE                     │
│  memory.add_tool_result(...)                    │
└────────────────────┬────────────────────────────┘
                     │
                     │ Loop back
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        ITERATION 3: THINK                       │
│  client.messages.create(...)                    │
└────────────────────┬────────────────────────────┘
                     │
                     │ Response:
                     │ stop_reason = "end_turn"
                     │ content = "I've saved Tokyo's
                     │            weather to tokyo.txt..."
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│        FINISH                                   │
│  return extract_text(response.content)          │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
                 USER SEES ANSWER
```

---


## 🎨 Three Levels: Feature Comparison

```
┌──────────────────────────────────────────────────────────────────────┐
│                           SIMPLE                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │
│  │    THINK    │ ───→ │     ACT     │ ───→ │   OBSERVE   │          │
│  │  (API call) │      │ (run tool)  │      │ (save result)│          │
│  └─────────────┘      └─────────────┘      └─────────────┘          │
│         ▲                                           │                 │
│         │                                           │                 │
│         └───────────────────────────────────────────┘                 │
│                      Basic loop                                       │
│                                                                       │
│  Features:                                                            │
│  ✅ Core ReAct loop                                                  │
│  ✅ 5 tools (search, calc, file, weather, wiki)                      │
│  ✅ Conversation memory                                               │
│  ✅ Pretty terminal output                                            │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────┐
│                        INTERMEDIATE                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │
│  │    THINK    │ ───→ │     ACT     │ ───→ │   OBSERVE   │          │
│  │  (STREAMED) │      │ (+ RETRY)   │      │ (save result)│          │
│  └─────────────┘      └─────────────┘      └─────────────┘          │
│         ▲                    │                      │                 │
│         │                    │ Retry on error      │                 │
│         │                    ↓                      │                 │
│         │             ┌─────────────┐               │                 │
│         │             │   RETRY 1   │               │                 │
│         │             └─────────────┘               │                 │
│         │                    │                      │                 │
│         │                    ↓                      │                 │
│         │             ┌─────────────┐               │                 │
│         │             │   RETRY 2   │               │                 │
│         │             └─────────────┘               │                 │
│         │                                           │                 │
│         └───────────────────────────────────────────┘                 │
│                                                                       │
│  Everything from Simple, PLUS:                                        │
│  ✅ Streaming output (tokens appear live)                            │
│  ✅ Auto-retry failed tools (MAX_RETRIES=2)                          │
│  ✅ Token usage tracking                                              │
│  💰 Cost estimation per run                                          │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────┐
│                          ADVANCED                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│         ┌─────────────────┐                                           │
│         │   📋 PLAN       │  ← NEW: Plan before acting                │
│         └────────┬────────┘                                           │
│                  │                                                    │
│                  ▼                                                    │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐          │
│  │    THINK    │ ───→ │     ACT     │ ───→ │   OBSERVE   │          │
│  │  (STREAMED) │      │ (+ RETRY)   │      │ (+ CACHE)   │          │
│  └─────────────┘      └─────────────┘      └─────────────┘          │
│         ▲                    │                      │                 │
│         │                    ↓                      │                 │
│         │             ┌─────────────┐               │                 │
│         │             │   CACHE?    │               │                 │
│         │             │  ┌────┐     │               │                 │
│         │             │  │ HIT│ ────┼───────────────┘ ← Instant!     │
│         │             │  └────┘     │                                 │
│         │             │   MISS      │                                 │
│         │             │    ↓        │                                 │
│         │             │  Run tool   │                                 │
│         │             │    ↓        │                                 │
│         │             │  Store in   │                                 │
│         │             │  cache      │                                 │
│         │             └─────────────┘                                 │
│         │                                           │                 │
│         └───────────────────────────────────────────┘                 │
│                                                                       │
│  Everything from Intermediate, PLUS:                                  │
│  ✅ Plan-first approach (structured reasoning)                       │
│  ✅ Tool result caching (speed + cost savings)                        │
│  ✅ Evaluation harness (automated testing)                            │
│  🎯 Better for complex multi-step tasks                              │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Stop Reason Decision Tree

```
                     Call Claude API
                           │
                           ▼
                  What is stop_reason?
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌───────────┐     ┌──────────┐      ┌──────────────┐
  │ "end_turn"│     │"tool_use"│      │ "max_tokens" │
  └─────┬─────┘     └────┬─────┘      └──────┬───────┘
        │                │                    │
        ▼                ▼                    ▼
   ┌─────────┐     ┌──────────┐         ┌─────────────┐
   │ FINISH  │     │  ACT +   │         │ Increase    │
   │         │     │ OBSERVE  │         │ max_tokens  │
   │ Extract │     │          │         │ and retry   │
   │ text    │     │ 1. Run   │         └─────────────┘
   │ Return  │     │    tool  │
   │ to user │     │ 2. Save  │
   └─────────┘     │    result│
                   │ 3. Loop  │
                   │    back  │
                   └──────────┘
```

---

## 🧠 How Planning Works (Advanced)

```
WITHOUT PLANNING (Simple/Intermediate):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task: "Research AI history and save report"

Iteration 1: "I'll search for AI history"
            → web_search("AI history")

Iteration 2: "I should also check Wikipedia"
            → wikipedia_search("Artificial Intelligence")

Iteration 3: "What about machine learning?"
            → wikipedia_search("Machine Learning")

Iteration 4: "Hmm, I should organize this..."
            → (realizes structure needs work)

Iteration 5: "Now I'll write the file"
            → file_io(write, "report.txt", ...)

Result: Works, but inefficient and sometimes disorganized


WITH PLANNING (Advanced):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task: "Research AI history and save report"

┌──────────────────────────────────────┐
│  📋 PLANNING PHASE (separate call)   │
├──────────────────────────────────────┤
│  Plan:                               │
│  1. Search for "AI history timeline" │
│  2. Look up key topics on Wikipedia: │
│     - Turing Test                    │
│     - Neural Networks                │
│     - Deep Learning                  │
│  3. Organize into chronological      │
│     sections                         │
│  4. Write comprehensive report       │
│     to ai_history.txt                │
│  READY                               │
└──────────────────────────────────────┘
           │
           │ Plan injected into task
           ▼
┌──────────────────────────────────────┐
│  EXECUTION PHASE (ReAct loop)        │
├──────────────────────────────────────┤
│  Iteration 1: Execute step 1         │
│  Iteration 2: Execute step 2a        │
│  Iteration 3: Execute step 2b        │
│  Iteration 4: Execute step 2c        │
│  Iteration 5: Execute step 3         │
│  Iteration 6: Execute step 4         │
│  DONE                                │
└──────────────────────────────────────┘

Result: More focused, organized, efficient
```

---

## 💾 Caching Mechanism (Advanced)

```
┌────────────────────────────────────────────────────────────┐
│                  tools/registry.py                         │
└────────────────────────────────────────────────────────────┘

_cache = {}  # In-memory cache

def dispatch(tool_name, tool_input):
    
    # Create cache key
    cache_key = f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}"
    # Example: "get_weather:{'city':'Tokyo'}"
    
    
    # Check if tool is cacheable
    if tool_name in _NO_CACHE:  # file_io is not cached!
        return run_tool(tool_name, tool_input)
    
    
    # Check cache
    if cache_key in _cache:
        return f"[cached] {_cache[cache_key]}", False  ← INSTANT!
    
    
    # Cache miss - run the tool
    result = run_tool(tool_name, tool_input)
    
    
    # Store in cache
    _cache[cache_key] = result
    
    
    return result, False


Example:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Call 1: get_weather(city="Tokyo")
    ├─ Cache miss
    ├─ Call API (takes 2 seconds)
    ├─ Store result in cache
    └─ Return "Tokyo: 15°C..."

Call 2: get_weather(city="London")
    ├─ Cache miss (different city!)
    ├─ Call API (takes 2 seconds)
    └─ Return "London: 12°C..."

Call 3: get_weather(city="Tokyo")
    ├─ Cache HIT!
    ├─ Return "[cached] Tokyo: 15°C..." ← INSTANT!
    └─ No API call, no cost, no delay

Benefits:
✅ Faster execution
✅ Lower API costs
✅ Reduced network failures
```

---

## 📊 Comparison: Message Sizes

```
SIMPLE (No streaming):
━━━━━━━━━━━━━━━━━━━━━━
User sees nothing...
User sees nothing...
User sees nothing...
[2 seconds pass]
BOOM! All text appears at once
"The weather in Tokyo is 15°C..."


INTERMEDIATE (With streaming):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The
The weather
The weather in
The weather in Tokyo
The weather in Tokyo is
The weather in Tokyo is 15
The weather in Tokyo is 15°C
The weather in Tokyo is 15°C with
[Text appears smoothly in real-time]
```

---

## 🎯 Key Architectural Principles

### 1. Separation of Concerns
```
main.py          → Entry point only
runner.py        → User interface only
loop.py          → ReAct logic only
memory/          → Message storage only
tools/           → Tool implementations only
utils/           → Helper functions only
```

### 2. Stateless Agent, Stateful Memory
```
Agent (loop.py)  → Stateless, pure function
Memory (buffer.py) → Stores all state
```

### 3. Tool Independence
```
Each tool is self-contained:
- Doesn't know about other tools
- Doesn't know about the agent
- Just: input → output
```

### 4. Error Handling at Boundaries
```
Tools return: (result, is_error)
Agent decides what to do with errors
Claude sees errors as normal tool results
```

---

## 🎓 Summary

**Key Architecture Points:**

1. **Simple Loop:** THINK → ACT → OBSERVE → Repeat
2. **Memory is Central:** Every API call includes full history
3. **Tools are Plugins:** Register once, dispatch by name
4. **Progressive Enhancement:** Simple → +Features → +More Features
5. **Clean Separation:** Each component has one job

**Most Important Files:**
- `agent/loop.py` - The ReAct loop (100 lines)
- `tools/registry.py` - Tool system (50 lines)
- `memory/buffer.py` - Message storage (40 lines)

**Total core code:** ~200 lines to understand the entire system!

---

For detailed code explanations, see [CODE_WALKTHROUGH.md](./CODE_WALKTHROUGH.md)

For learning guide, see [BEGINNERS_GUIDE.md](./BEGINNERS_GUIDE.md)

For quick start, see [QUICK_START.md](./QUICK_START.md)
