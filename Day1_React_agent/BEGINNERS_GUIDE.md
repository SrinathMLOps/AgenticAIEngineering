# Complete Beginner's Guide to ReAct Agent

## 🎯 What Is This Project?

This is a **learning project** that teaches you how to build AI agents from scratch using the **ReAct pattern** (Reasoning + Acting). You'll build agents that can:
- Think step-by-step
- Use tools (search web, calculate, read/write files, get weather, lookup Wikipedia)
- Learn from tool results and decide what to do next

The project has **three progressive levels**: Simple → Intermediate → Advanced

---

## 📚 What is the ReAct Pattern?

**ReAct** = **Rea**soning + **Act**ing

Traditional AI just answers questions. ReAct agents follow a loop:

```
1. THINK  → "What should I do next?"
2. ACT    → "I'll use the search tool"
3. OBSERVE → "Here's what the tool returned"
4. THINK  → "Based on that result, what's next?"
... repeat until the task is complete
```

### Real Example:
**User:** "What's the weather in Tokyo and save it to a file?"

**Agent's ReAct Loop:**
```
STEP 1:
  THINK:  "I need to get Tokyo's weather first"
  ACT:    Call get_weather(city="Tokyo")
  OBSERVE: "Tokyo: 15°C, Cloudy, 7-day forecast: ..."

STEP 2:
  THINK:  "Got the weather, now I'll save it"
  ACT:    Call file_io(action="write", path="tokyo_weather.txt", content="...")
  OBSERVE: "Successfully wrote to tokyo_weather.txt"

STEP 3:
  THINK:  "Task complete!"
  FINISH: "I've saved Tokyo's weather to tokyo_weather.txt..."
```

---

## 🗂️ Project Structure


```
day_1_react_agent/
│
├── simple/              ← START HERE! Basic ReAct loop
├── intermediate/        ← Adds streaming, retry, cost tracking
├── advanced/            ← Adds planning, caching, evaluation
│
└── README.md            ← Quick reference (you are reading BEGINNERS_GUIDE.md)
```

Each folder is **completely independent** — you can copy any folder elsewhere and it will work.

---

## 🚀 Quick Start (5 minutes)

### Step 1: Choose Your Level
Start with `simple/`:
```bash
cd simple
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup API Key
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Get a key:** https://console.anthropic.com/

### Step 5: Run!
```bash
python main.py
```

You'll see an interactive menu. Try: **"What is the weather in London?"**



---

## 📖 Understanding Each Level

### 🟢 Level 1: Simple

**What you learn:**
- The core ReAct loop (THINK → ACT → OBSERVE)
- How to call Claude API with tools
- How to dispatch tool calls
- How to maintain conversation memory

**Files to Read (in order):**

1. **`main.py`** (5 lines)
   - Entry point
   - Loads environment variables
   - Calls the runner

2. **`agent/runner.py`**
   - Interactive menu
   - Example tasks you can try

3. **`agent/loop.py`** ⭐ **MOST IMPORTANT FILE**
   - The ReAct loop implementation
   - Study this carefully!

4. **`tools/registry.py`**
   - Registers all available tools
   - Dispatches tool calls by name

5. **`tools/weather.py`** and **`tools/wikipedia.py`**
   - Examples of how to create tools
   - One calls a REST API, one uses a Python library

6. **`memory/buffer.py`**
   - Stores conversation history
   - Formats messages for Claude API

7. **`utils/logger.py`**
   - Pretty-prints THINK/ACT/OBSERVE panels
   - Makes the terminal output readable

**Key Concepts:**
```python
# The main loop structure
for step in range(1, MAX_STEPS + 1):
    # THINK: call Claude API
    response = client.messages.create(
        model=MODEL,
        tools=tools,
        messages=memory.get_messages()
    )
    
    # Check what Claude wants to do
    if response.stop_reason == "end_turn":
        return final_answer  # DONE!
    
    if response.stop_reason == "tool_use":
        # ACT: run the tool
        result = dispatch(tool_name, tool_input)
        
        # OBSERVE: add result to memory
        memory.add_tool_result(tool_id, result)
        # Loop continues...
```



**Try These Tasks:**
```
1. "What is the current weather in Tokyo?"
2. "Who invented the World Wide Web? Look it up on Wikipedia."
3. "Calculate 25 * 47 + 183"
4. "Search the web for Python web frameworks and save the top 3 to frameworks.txt"
```

---

### 🟡 Level 2: Intermediate

**What's NEW:**
1. **Streaming Output** - See tokens appear live (not all at once)
2. **Retry on Error** - Auto-retry failed tool calls
3. **Token Usage Tracker** - See cost after each run

**Files to Compare:**
- `agent/loop.py` - Look for `# NEW` comments
- `utils/logger.py` - Added `log_token_usage()` function

**Key Changes:**

#### 1. Streaming Output
```python
# Before (Simple): Wait for full response
response = client.messages.create(...)

# After (Intermediate): Tokens appear live
with client.messages.stream(**kwargs) as stream:
    for token in stream.text_stream:
        print(token, end="", flush=True)
    response = stream.get_final_message()
```

Toggle with: `STREAM_OUTPUT=false` in `.env`

#### 2. Retry Logic
```python
def _dispatch_with_retry(tool_name, tool_input):
    result, is_error = dispatch(tool_name, tool_input)
    
    if not is_error:
        return result, False
    
    # Retry on error
    for attempt in range(1, MAX_RETRIES + 1):
        result, is_error = dispatch(tool_name, tool_input)
        if not is_error:
            return result, False
    
    return result, is_error  # Give up
```

Set `MAX_RETRIES=0` in `.env` to disable

#### 3. Token Tracking
```python
# Accumulate across all API calls
total_input_tokens += response.usage.input_tokens
total_output_tokens += response.usage.output_tokens

# Show at the end
log_token_usage(total_input_tokens, total_output_tokens)
```



**Try These Tasks:**
```
1. "Explain how HTTPS works" - watch streaming in action
2. "Search for the top 5 Python libraries for data science" - see retry recover errors
3. "Look up quantum computing on Wikipedia and save a summary" - check token cost
```

---

### 🔴 Level 3: Advanced

**What's NEW:**
1. **Plan-First Approach** - Agent creates a numbered plan before acting
2. **Tool Result Caching** - Same tool call = instant cached result
3. **Evaluation Harness** - Automated testing with pass/fail scoring

**Files to Study:**
- `agent/loop.py` - Look for `_plan_phase()` function
- `tools/registry.py` - Look for caching logic
- `eval_harness.py` - Automated evaluation script

**Key Changes:**

#### 1. Plan-First
```python
def _plan_phase(client, task):
    """Ask model to create a plan before the loop"""
    response = client.messages.create(
        model=MODEL,
        messages=[{
            "role": "user", 
            "content": f"Task: {task}\n\n{_PLAN_PROMPT}"
        }]
    )
    
    plan = extract_text(response.content)
    log_plan(plan)  # Shows magenta 📋 PLAN panel
    return plan

# Then inject plan into task
task = f"{task}\n\n[Your plan]\n{plan}\n\nNow execute step by step."
```

Toggle with: `PLAN_FIRST=false` in `.env`

#### 2. Tool Caching
```python
# In tools/registry.py
_cache = {}  # Store results

def dispatch(tool_name, tool_input):
    # Create cache key
    cache_key = f"{tool_name}:{json.dumps(tool_input, sort_keys=True)}"
    
    # Check cache
    if tool_name not in _NO_CACHE and cache_key in _cache:
        return f"[cached] {_cache[cache_key]}", False
    
    # Run tool
    result = run_tool(tool_name, tool_input)
    
    # Store in cache
    _cache[cache_key] = result
    return result, False
```

**Note:** `file_io` is excluded from cache (side effects!)



#### 3. Evaluation Harness
```bash
cd advanced
python eval_harness.py
```

Runs 5 test tasks and scores them:
```
Task 1: Calculate 123 * 456 ................................ PASS ✓
Task 2: Get weather for Paris ............................. PASS ✓
Task 3: Wikipedia lookup for Python ........................ PASS ✓
Task 4: Multi-step research task ........................... PASS ✓
Task 5: Complex reasoning task ............................. FAIL ✗

RESULTS: 4/5 passed (80% accuracy)
```

Results saved to `eval_results.json`

**Try These Tasks:**
```
1. "Research the history of AI: milestones, key people, current state. Save a report."
   - Watch the plan appear first!

2. "Who created Python? What's Python used for? Save both answers."
   - Second Wikipedia call will be cached

3. python eval_harness.py
   - Run the full benchmark
```

---

## 🛠️ Available Tools

All three levels have these tools:

| Tool | What It Does | Example |
|------|--------------|---------|
| `web_search` | Search the web via DuckDuckGo | "latest news about AI" |
| `calculator` | Evaluate math expressions | "123 * 456 + 789" |
| `file_io` | Read/write files | read/write/append operations |
| `get_weather` | Get weather for any city | "Tokyo", "London", "NYC" |
| `wikipedia_search` | Wikipedia article summary | "Python programming", "Albert Einstein" |

---

## 📁 File Structure Explained

```
simple/  (or intermediate/ or advanced/)
│
├── main.py                  # Entry point - run this!
├── requirements.txt         # Python dependencies
├── .env                     # YOUR API KEY GOES HERE
├── .env.example             # Template for .env
│
├── agent/
│   ├── loop.py             # ⭐ THE REACT LOOP (study this!)
│   └── runner.py           # Interactive menu + example tasks
│
├── memory/
│   └── buffer.py           # Stores conversation history
│
├── tools/
│   ├── registry.py         # Registers + dispatches tools
│   ├── calculator.py       # Math evaluation tool
│   ├── file_io.py          # File read/write tool
│   ├── search.py           # Web search tool
│   ├── weather.py          # Weather API tool
│   └── wikipedia.py        # Wikipedia lookup tool
│
└── utils/
    ├── logger.py           # Pretty terminal output
    └── schema.py           # Pydantic models for type safety
```



---

## 🎓 How to Learn From This Code

### For Complete Beginners:

**Week 1: Understand Simple**
1. Read `README.md` in the `simple/` folder
2. Run `python main.py` and try 3-4 tasks
3. Read `agent/loop.py` line by line (it's only ~90 lines!)
4. Read `tools/weather.py` to see how a tool is made
5. Modify the system prompt and see how behavior changes

**Week 2: Study Intermediate**
1. Compare `simple/agent/loop.py` vs `intermediate/agent/loop.py`
2. Search for `# NEW` comments
3. Toggle `STREAM_OUTPUT` and `MAX_RETRIES` in `.env` to see the difference
4. Run a complex task and check token usage

**Week 3: Explore Advanced**
1. Compare `intermediate/agent/loop.py` vs `advanced/agent/loop.py`
2. Understand the plan-first approach
3. Study caching in `tools/registry.py`
4. Run `python eval_harness.py`
5. Create your own eval task!

---

### For Experienced Developers:

**Day 1:**
- Clone repo, setup all three levels
- Read all three `agent/loop.py` files in parallel
- Understand the progression: Simple → +Streaming/Retry → +Planning/Caching
- Run eval harness

**Day 2:**
- Add a new tool (e.g., email sender, database query, image generator)
- Modify the system prompt for a specialized agent
- Experiment with different Claude models

**Day 3:**
- Integrate with your own API
- Add persistent memory (database instead of in-memory buffer)
- Build a multi-agent system

---

## 🔧 Configuration (.env file)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional - Common Settings
MODEL=claude-sonnet-4-20250514              # Which Claude model to use
MAX_STEPS=15                                 # Max iterations before giving up

# Optional - Intermediate+
MAX_RETRIES=2                                # Retry failed tools (0 to disable)
STREAM_OUTPUT=true                           # Stream tokens live (false = wait for full)

# Optional - Advanced only
PLAN_FIRST=true                              # Create plan before acting
```



---

## 💡 Key Concepts Explained

### 1. What is a "Tool"?

A tool is a Python function that:
- Has a clear name and description
- Defines input parameters (schema)
- Returns a string result
- Is registered in `tools/registry.py`

**Example: Weather Tool**
```python
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    # Call weather API
    data = requests.get(f"https://api.open-meteo.com/...")
    # Format result
    return f"{city}: {data['temp']}°C, {data['condition']}"

# Register it
TOOL_FUNCTIONS = {
    "get_weather": get_weather
}
```

Claude sees:
```json
{
  "name": "get_weather",
  "description": "Get current weather for a city",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {"type": "string"}
    }
  }
}
```

### 2. What is "Conversation Memory"?

The agent needs to remember the conversation to make decisions. Memory format:

```python
[
  {"role": "user", "content": "What's the weather in Tokyo?"},
  {"role": "assistant", "content": [
    {"type": "text", "text": "I'll check the weather"},
    {"type": "tool_use", "id": "123", "name": "get_weather", "input": {"city": "Tokyo"}}
  ]},
  {"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "123", "content": "Tokyo: 15°C, Cloudy"}
  ]},
  {"role": "assistant", "content": "The weather in Tokyo is 15°C and cloudy"}
]
```

Each API call includes this entire history!

### 3. What is `stop_reason`?

When Claude responds, it tells you WHY it stopped:

| stop_reason | Meaning | What to do |
|-------------|---------|------------|
| `end_turn` | "I'm done, here's my final answer" | Return the answer to user |
| `tool_use` | "I need to call a tool" | Extract tool call, run it, loop |
| `max_tokens` | "I ran out of token budget" | Increase `max_tokens` |



### 4. How Does Planning Help?

**Without Planning (Simple/Intermediate):**
```
User: "Research AI history and save a report"

Step 1: "I'll search for AI history" → web_search
Step 2: "Now I'll look up deep learning" → web_search
Step 3: "Let me check neural networks" → wikipedia_search
Step 4: "I should probably organize this..." → (realizes structure is messy)
Step 5: "Let me write the file" → file_io
```

**With Planning (Advanced):**
```
📋 PLAN:
1. Search for "AI history timeline"
2. Look up 3 key topics on Wikipedia: Turing, Neural Networks, Deep Learning
3. Organize findings into sections
4. Write comprehensive report to ai_history.txt

[Then executes plan step-by-step with focus]
```

Result: More organized, fewer wasted steps, better output!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
# Make sure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### "AuthenticationError: Invalid API key"
```bash
# Check .env file exists
ls .env  # Should exist

# Check it has your key
cat .env  # Should show: ANTHROPIC_API_KEY=sk-ant-...

# Get a key at: https://console.anthropic.com/
```

### "Agent reached maximum steps without completing"
```bash
# Increase max steps in .env
MAX_STEPS=25  # Default is 15
```

### Tool calls fail repeatedly
```bash
# Check internet connection
# Check if specific API is down (weather, Wikipedia)

# Disable retry to see raw error
MAX_RETRIES=0
```

---

## 🚀 Next Steps: Customize Your Agent

### Add a New Tool

**Example: Add a "translate" tool**

1. Create `tools/translator.py`:
```python
def translate_text(text: str, target_language: str) -> str:
    """Translate text to another language"""
    # Use Google Translate API or similar
    result = translate_api(text, target_language)
    return f"Translation: {result}"
```

2. Register in `tools/registry.py`:
```python
from tools.translator import translate_text

TOOL_FUNCTIONS = {
    # ... existing tools ...
    "translate_text": translate_text
}

# Add definition
{
    "name": "translate_text",
    "description": "Translate text to another language",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "target_language": {"type": "string"}
        },
        "required": ["text", "target_language"]
    }
}
```

3. Test it!
```bash
python main.py
> "Translate 'Hello World' to Spanish"
```



### Create a Specialized Agent

Modify the `SYSTEM_PROMPT` in `agent/loop.py`:

**Example: Research Assistant**
```python
SYSTEM_PROMPT = """You are a thorough research assistant.

Your approach:
1. Always search multiple sources
2. Cross-reference information
3. Cite sources in your final answer
4. Save detailed reports to files

Available tools: web_search, wikipedia_search, file_io, calculator

Be comprehensive and academic in tone."""
```

**Example: Data Analyst**
```python
SYSTEM_PROMPT = """You are a data analyst specializing in calculations and insights.

Your approach:
1. Always use the calculator for math (never estimate)
2. Show your work step-by-step
3. Provide data visualizations when possible
4. Save analysis results to files

Available tools: calculator, file_io, web_search

Be precise and data-driven."""
```

---

## 📊 Understanding Token Costs

**From intermediate/advanced levels:**

```
╭─ 💰 TOKEN USAGE ─────────────────────────────────╮
│ Input:  2,345 tokens                              │
│ Output:   567 tokens                              │
│ Total:  2,912 tokens                              │
│                                                   │
│ Estimated cost: $0.0437 USD                       │
╰───────────────────────────────────────────────────╯
```

**Pricing (Claude Sonnet 4.0):**
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Tips to reduce costs:**
1. Use caching (Advanced level)
2. Keep system prompts concise
3. Limit MAX_STEPS for simple tasks
4. Clear conversation memory when starting new tasks

---

## 🎯 Practice Tasks

### Beginner Tasks
```
1. "What is the weather in Paris today?"
2. "Calculate the area of a circle with radius 7"
3. "Look up 'Python programming' on Wikipedia"
4. "Search for the top 3 JavaScript frameworks"
5. "Save 'Hello World' to test.txt"
```

### Intermediate Tasks
```
1. "Find the population of Tokyo and calculate 10% of it"
2. "Research React vs Vue and save a comparison"
3. "What's the weather in London? Save it to weather.txt"
4. "Look up 'Machine Learning' and explain it in simple terms"
5. "Calculate compound interest: $1000 at 5% for 10 years"
```

### Advanced Tasks
```
1. "Research the history of the Internet: key milestones, inventors, and impact. Save a detailed report."

2. "Compare Python, JavaScript, and Go: look up each on Wikipedia, search for their popularity, calculate their age, and save a structured comparison."

3. "Plan a 3-day trip to Tokyo: get weather forecast, research top attractions, and save an itinerary."

4. "Analyze the Fibonacci sequence: explain it, calculate the 20th number, and save examples."

5. "Create a comprehensive guide on quantum computing: research basics, applications, and current state. Save to quantum_guide.txt"
```



---

## 🎓 Advanced Topics

### 1. Multi-Agent Systems

Create multiple specialized agents:
```python
research_agent = Agent(system_prompt=RESEARCH_PROMPT)
analysis_agent = Agent(system_prompt=ANALYSIS_PROMPT)
writing_agent = Agent(system_prompt=WRITING_PROMPT)

# Coordinate them
research_result = research_agent.run("Research AI history")
analysis = analysis_agent.run(f"Analyze: {research_result}")
final_report = writing_agent.run(f"Write report: {analysis}")
```

### 2. Persistent Memory

Replace `memory/buffer.py` with database storage:
```python
import sqlite3

class DatabaseMemory:
    def __init__(self, session_id):
        self.db = sqlite3.connect("agent_memory.db")
        self.session_id = session_id
    
    def add_message(self, role, content):
        self.db.execute(
            "INSERT INTO messages VALUES (?, ?, ?)",
            (self.session_id, role, json.dumps(content))
        )
    
    def get_messages(self):
        cursor = self.db.execute(
            "SELECT role, content FROM messages WHERE session_id = ?",
            (self.session_id,)
        )
        return [{"role": row[0], "content": json.loads(row[1])} for row in cursor]
```

### 3. Prompt Caching

Use Anthropic's prompt caching to reduce costs:
```python
response = client.messages.create(
    model=MODEL,
    system=[
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}  # Cache this!
        }
    ],
    messages=memory.get_messages()
)
```

Subsequent calls with the same system prompt are cheaper!

---

## 📚 Resources

### Official Documentation
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Claude Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)

### Related Projects
- [LangChain](https://github.com/langchain-ai/langchain) - Framework for LLM apps
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Autonomous GPT agent
- [BabyAGI](https://github.com/yoheinakajima/babyagi) - AI task management

### Papers
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)

---

## ❓ FAQ

**Q: Do I need paid API access?**
A: Yes, you need an Anthropic API key. New accounts get $5 free credit.

**Q: Which level should I start with?**
A: Always start with `simple/`. It has the core concepts.

**Q: Can I use GPT-4 instead of Claude?**
A: The project uses Anthropic's API, but you can adapt it for OpenAI with minimal changes.

**Q: How is this different from LangChain?**
A: This is educational bare-metal code. LangChain is a production framework. Learn here first!

**Q: Can I use this in production?**
A: This is a learning project. For production, add error handling, logging, monitoring, security, etc.

**Q: How do I add authentication/security?**
A: Start with API key management, rate limiting, input validation, and sandboxed tool execution.

**Q: Can agents call other agents?**
A: Yes! Create a "call_agent" tool that dispatches to another agent instance.

**Q: How do I make it faster?**
A: Use caching (advanced), parallel tool calls, smaller models, or prompt optimization.

---

## 🤝 Contributing Ideas

Want to extend this project? Here are ideas:

1. **New Tools:**
   - Email sender (Gmail API)
   - Database queries (SQL)
   - Image generation (DALL-E)
   - Code execution (sandbox)
   - Slack/Discord integration

2. **New Features:**
   - Conversation history UI (web interface)
   - Voice input/output
   - Image understanding
   - Streaming tool results
   - Multi-agent collaboration

3. **Improvements:**
   - Better error messages
   - Progress bars
   - Logging to file
   - Metrics dashboard
   - Unit tests

---

## 🎉 Conclusion

You now have a complete understanding of how ReAct agents work!

**Your learning path:**
1. ✅ Understand the ReAct pattern (THINK → ACT → OBSERVE)
2. ✅ Run and study the Simple implementation
3. ✅ Progress through Intermediate and Advanced
4. ✅ Customize tools and system prompts
5. ✅ Build your own specialized agent!

**Remember:**
- Start with `simple/`
- Read `agent/loop.py` carefully
- Experiment with different tasks
- Modify and break things to learn
- Build your own tools

Happy coding! 🚀

---

**Questions or issues?**
- Check the main README.md
- Review the code comments (they're detailed!)
- Experiment with different tasks
- Try modifying the system prompt

**Want to go deeper?**
- Study `tools/registry.py` for tool dispatch patterns
- Read `memory/buffer.py` for conversation management
- Explore `utils/logger.py` for terminal formatting
- Run `eval_harness.py` (advanced) to see automated testing

