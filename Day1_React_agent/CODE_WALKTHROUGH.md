# 🔍 Code Walkthrough - Understanding Every Part

This document walks through the ENTIRE codebase, explaining what each file does and how they work together.

---

## 📋 Table of Contents

1. [Entry Point: main.py](#entry-point-mainpy)
2. [Agent Runner: agent/runner.py](#agent-runner-agentrunnerpy)
3. [The Heart: agent/loop.py](#the-heart-agentlooppy)
4. [Memory System: memory/buffer.py](#memory-system-memorybufferpy)
5. [Tool System: tools/registry.py](#tool-system-toolsregistrypy)
6. [Individual Tools](#individual-tools)
7. [Utilities: utils/](#utilities-utils)

---

## Entry Point: main.py

**File:** `simple/main.py` (5 lines!)

```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file → makes ANTHROPIC_API_KEY available

from agent.runner import run_interactive, run_single
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command-line mode: python main.py "your task here"
        run_single(" ".join(sys.argv[1:]))
    else:
        # Interactive mode: python main.py
        run_interactive()
```

**What it does:**
1. Loads environment variables from `.env`
2. Checks if you provided a task as command-line argument
3. Runs either single-task or interactive mode

**Try it:**
```bash
python main.py "What's the weather in Tokyo?"  # Single task
python main.py                                  # Interactive menu
```

---

## Agent Runner: agent/runner.py

**File:** `simple/agent/runner.py`

```python
from rich.console import Console
from agent.loop import run_agent

console = Console()

def run_single(task: str):
    """Run one task and exit"""
    console.print(f"\n[bold cyan]Task:[/bold cyan] {task}\n")
    result = run_agent(task)  # ← The magic happens here!
    console.print(f"\n[bold green]Result:[/bold green] {result}\n")

def run_interactive():
    """Interactive menu with example tasks"""
    console.print("[bold blue]ReAct Agent - Simple[/bold blue]\n")
    
    examples = [
        "What is the weather in Tokyo?",
        "Calculate 15 * 23 + 67",
        "Look up 'Python programming' on Wikipedia",
        "Search for top JavaScript frameworks",
        "Custom task..."
    ]
    
    # Show menu...
    choice = console.input("Choose a task (1-5): ")
    
    if choice == "5":
        task = console.input("Enter your task: ")
    else:
        task = examples[int(choice) - 1]
    
    console.print(f"\n[bold cyan]Running:[/bold cyan] {task}\n")
    result = run_agent(task)
    console.print(f"\n[bold green]Final Result:[/bold green]\n{result}\n")
```

**What it does:**
1. Provides user interface (CLI menu or direct execution)
2. Calls `run_agent()` from `loop.py`
3. Displays results with pretty formatting

---


## The Heart: agent/loop.py

**File:** `simple/agent/loop.py` ⭐ **MOST IMPORTANT FILE**

### Part 1: Setup and Configuration

```python
import os
import anthropic
from memory.buffer import ConversationBuffer
from tools.registry import dispatch, get_tool_definitions
from utils.logger import log_act, log_finish, log_observe, log_step, log_think

# Configuration from .env
MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))

SYSTEM_PROMPT = """You are a capable AI agent that solves tasks step by step.

You have access to tools: web_search, calculator, file_io, get_weather, wikipedia_search.

## How to behave
- Think carefully before acting. Use tools only when needed.
- After each tool result, reflect on what you learned.
- When you have enough information, respond with your final answer.
...
"""
```

**Key Points:**
- `MODEL`: Which Claude model to use
- `MAX_STEPS`: Safety limit to prevent infinite loops
- `SYSTEM_PROMPT`: Instructions that guide Claude's behavior

---

### Part 2: The Main Loop Function

```python
def run_agent(task: str) -> str:
    """Run the ReAct loop for a given task. Returns the final answer."""
    
    # 1. Initialize API client
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # 2. Initialize conversation memory
    memory = ConversationBuffer()
    memory.add_user(task)  # Add the user's task
    
    # 3. Get tool definitions
    tools = get_tool_definitions()  # From registry.py
    
    # 4. THE MAIN LOOP
    for step in range(1, MAX_STEPS + 1):
        log_step(step, MAX_STEPS)  # Show "Step 1/15" in terminal
        
        # ... (see next section)
```

**What happens:**
1. Create Anthropic API client
2. Initialize memory with user's task
3. Get list of available tools
4. Start the loop (max 15 iterations)

---

### Part 3: THINK - Call Claude API

```python
        # ── THINK ──
        response = client.messages.create(
            model=MODEL,                    # "claude-sonnet-4-20250514"
            max_tokens=4096,                # Max length of response
            system=SYSTEM_PROMPT,           # Agent instructions
            tools=tools,                    # Available tool definitions
            messages=memory.get_messages()  # Conversation history
        )
        
        # Save Claude's response to memory
        memory.add_assistant(response.content)
```

**What happens:**
- Call Claude API with:
  - System prompt (agent instructions)
  - Tool definitions (what tools are available)
  - Conversation history (what happened so far)
- Claude thinks and decides what to do next
- Save Claude's response to memory

**Claude's response contains:**
- Text: reasoning about what to do
- Tool calls: if it wants to use a tool
- `stop_reason`: why it stopped generating

---

### Part 4: FINISH - Check if Done

```python
        # ── FINISHED ──
        if response.stop_reason == "end_turn":
            # Claude says: "I'm done, here's my final answer"
            final_text = _extract_text(response.content)
            log_think(final_text)
            log_finish(final_text)
            return final_text  # Return to user!
```

**What happens:**
- Check if `stop_reason == "end_turn"`
- This means Claude is done and has a final answer
- Extract the text and return it

---

### Part 5: ACT + OBSERVE - Execute Tools

```python
        # ── ACT + OBSERVE ──
        if response.stop_reason == "tool_use":
            # Claude says: "I want to call a tool"
            
            for block in response.content:
                # First, log any reasoning text
                if block.type == "text" and block.text:
                    log_think(block.text)
                
                # Then, handle tool calls
                if block.type == "tool_use":
                    tool_call = ToolCall(
                        id=block.id,           # "toolu_123abc"
                        name=block.name,       # "get_weather"
                        input=block.input      # {"city": "Tokyo"}
                    )
                    log_act(tool_call.name, tool_call.input)
                    
                    # ACT: Run the tool!
                    result, is_error = dispatch(tool_call.name, tool_call.input)
                    log_observe(result, is_error)
                    
                    # OBSERVE: Add result to memory so Claude can see it
                    memory.add_tool_result(tool_call.id, result, is_error)
            
            continue  # Go to next iteration of the loop
```

**What happens:**
1. Check if `stop_reason == "tool_use"`
2. Extract tool calls from response
3. For each tool call:
   - Log what we're doing (ACT panel)
   - Run the tool via `dispatch()`
   - Log the result (OBSERVE panel)
   - Add result to memory
4. Loop back to THINK step

---

### Part 6: Helper Functions

```python
def _extract_text(content: list) -> str:
    """Extract text from Claude's response content blocks"""
    parts = [block.text for block in content 
             if hasattr(block, "text") and block.text]
    return "\n".join(parts) if parts else "No text response."
```

**What it does:**
- Claude's response can have multiple blocks (text + tool_use)
- This function extracts just the text parts
- Joins them together

---


### Complete Loop Visualization

```python
def run_agent(task):
    client = anthropic.Anthropic(...)
    memory = ConversationBuffer()
    memory.add_user(task)
    tools = get_tool_definitions()
    
    for step in range(1, MAX_STEPS + 1):
        # ┌─────────────────────────────────────┐
        # │ STEP 1                              │
        # └─────────────────────────────────────┘
        
        # ╭─ 🤔 THINK ────────────────────────╮
        # │ I need to get Tokyo's weather     │
        # ╰───────────────────────────────────╯
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=memory.get_messages()
        )
        memory.add_assistant(response.content)
        
        if response.stop_reason == "end_turn":
            # ╭─ ✅ FINISH ───────────────────╮
            # │ Here's my final answer...     │
            # ╰───────────────────────────────╯
            return extract_text(response.content)
        
        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    # ╭─ 🔧 ACT ──────────────────────╮
                    # │ get_weather(city="Tokyo")     │
                    # ╰───────────────────────────────╯
                    result, is_error = dispatch(block.name, block.input)
                    
                    # ╭─ 👁️ OBSERVE ──────────────────╮
                    # │ Tokyo: 15°C, Cloudy           │
                    # ╰───────────────────────────────╯
                    memory.add_tool_result(block.id, result, is_error)
            
            continue  # Loop back to THINK
```

---

## Memory System: memory/buffer.py

**File:** `simple/memory/buffer.py`

```python
class ConversationBuffer:
    """Stores the conversation history in the format Claude expects"""
    
    def __init__(self):
        self.messages = []  # List of message dicts
    
    def add_user(self, content: str):
        """Add a user message"""
        self.messages.append({
            "role": "user",
            "content": content
        })
    
    def add_assistant(self, content):
        """Add Claude's response (can be text + tool_use blocks)"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
    
    def add_tool_result(self, tool_use_id: str, result: str, is_error: bool):
        """Add a tool result so Claude can see what happened"""
        self.messages.append({
            "role": "user",  # Tool results come from "user" role
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result,
                "is_error": is_error
            }]
        })
    
    def get_messages(self):
        """Return the full message history"""
        return self.messages
```

### Example Memory State

After one tool call, memory looks like:

```python
[
    # Initial task
    {
        "role": "user",
        "content": "What's the weather in Tokyo?"
    },
    
    # Claude's first response
    {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "I'll check the weather for Tokyo."
            },
            {
                "type": "tool_use",
                "id": "toolu_123",
                "name": "get_weather",
                "input": {"city": "Tokyo"}
            }
        ]
    },
    
    # Tool result
    {
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "toolu_123",
            "content": "Tokyo: 15°C, Cloudy, Humidity: 65%",
            "is_error": False
        }]
    },
    
    # Claude's final response
    {
        "role": "assistant",
        "content": "The weather in Tokyo is 15°C and cloudy..."
    }
]
```

---


## Tool System: tools/registry.py

**File:** `simple/tools/registry.py`

### Part 1: Import All Tools

```python
from tools.calculator import calculate
from tools.file_io import file_io
from tools.search import web_search
from tools.weather import get_weather
from tools.wikipedia import wikipedia_search
```

### Part 2: Register Tool Functions

```python
TOOL_FUNCTIONS = {
    "calculator": calculate,
    "file_io": file_io,
    "web_search": web_search,
    "get_weather": get_weather,
    "wikipedia_search": wikipedia_search
}
```

This dict maps tool names → Python functions

### Part 3: Define Tool Schemas

```python
TOOL_DEFINITIONS = [
    {
        "name": "get_weather",
        "description": "Get current weather and 7-day forecast for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g. 'Tokyo', 'London')"
                }
            },
            "required": ["city"]
        }
    },
    # ... more tools
]
```

**What Claude sees:**
- Tool name: `get_weather`
- What it does: "Get current weather..."
- What parameters it needs: `city` (string, required)

### Part 4: The Dispatcher

```python
def dispatch(tool_name: str, tool_input: dict) -> tuple[str, bool]:
    """
    Run a tool by name.
    Returns: (result_string, is_error)
    """
    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool: {tool_name}", True
    
    try:
        # Get the function
        fn = TOOL_FUNCTIONS[tool_name]
        
        # Call it with the input dict as kwargs
        result = fn(**tool_input)
        
        # Return result + no error
        return str(result), False
        
    except Exception as e:
        # Return error message + error flag
        return f"Error: {str(e)}", True

def get_tool_definitions():
    """Return the list of tool schemas for Claude"""
    return TOOL_DEFINITIONS
```

**How it works:**
1. Look up the function in `TOOL_FUNCTIONS`
2. Call the function with the input parameters
3. Return the result as a string
4. If anything fails, return error message

**Example:**
```python
# Claude wants to call: get_weather(city="Tokyo")
result, is_error = dispatch("get_weather", {"city": "Tokyo"})
# result = "Tokyo: 15°C, Cloudy..."
# is_error = False
```

---

## Individual Tools

### Tool 1: calculator.py

**File:** `simple/tools/calculator.py`

```python
import ast
import operator

# Safe operators (no dangerous operations)
OPERATORS = {
    ast.Add: operator.add,      # +
    ast.Sub: operator.sub,      # -
    ast.Mult: operator.mul,     # *
    ast.Div: operator.truediv,  # /
    ast.Pow: operator.pow,      # **
    ast.Mod: operator.mod,      # %
}

def calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.
    
    Examples:
        "2 + 2" → 4.0
        "10 * 5 + 3" → 53.0
        "2 ** 8" → 256.0
    """
    try:
        # Parse expression into AST (Abstract Syntax Tree)
        tree = ast.parse(expression, mode='eval')
        
        # Evaluate the AST safely
        result = _eval_node(tree.body)
        
        return result
        
    except Exception as e:
        raise ValueError(f"Cannot calculate '{expression}': {e}")

def _eval_node(node):
    """Recursively evaluate AST nodes"""
    if isinstance(node, ast.Constant):
        # It's a number
        return node.value
    
    elif isinstance(node, ast.BinOp):
        # It's an operation (e.g., 2 + 3)
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op = OPERATORS.get(type(node.op))
        
        if op is None:
            raise ValueError(f"Unsupported operation: {type(node.op)}")
        
        return op(left, right)
    
    else:
        raise ValueError(f"Unsupported expression type: {type(node)}")
```

**Why AST instead of `eval()`?**
- `eval()` is dangerous: `eval("__import__('os').system('rm -rf /')")` 😱
- AST parsing only allows safe math operations
- No access to system functions, imports, etc.

---

### Tool 2: weather.py

**File:** `simple/tools/weather.py`

```python
import requests

def get_weather(city: str) -> str:
    """
    Get current weather and 7-day forecast for a city.
    Uses Open-Meteo API (free, no key needed).
    """
    try:
        # 1. Convert city name to coordinates (geocoding)
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = requests.get(
            geocode_url,
            params={"name": city, "count": 1, "language": "en"}
        )
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return f"City '{city}' not found."
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        
        # 2. Get weather data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min",
                "timezone": "auto",
                "forecast_days": 7
            }
        )
        weather_data = weather_response.json()
        
        # 3. Format the result
        current = weather_data["current"]
        daily = weather_data["daily"]
        
        result = f"Weather in {city}:\n"
        result += f"Current: {current['temperature_2m']}°C, "
        result += f"Humidity: {current['relative_humidity_2m']}%\n\n"
        result += "7-day forecast:\n"
        
        for i in range(7):
            date = daily["time"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            result += f"{date}: {min_temp}°C to {max_temp}°C\n"
        
        return result
        
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"
```

**How it works:**
1. Geocode: Convert "Tokyo" → latitude/longitude
2. API call: Get weather data for those coordinates
3. Format: Create readable text response

---


### Tool 3: wikipedia.py

**File:** `simple/tools/wikipedia.py`

```python
import wikipediaapi

# Initialize Wikipedia API client
wiki = wikipediaapi.Wikipedia(
    user_agent='ReAct-Agent/1.0',
    language='en'
)

def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia and return a summary.
    
    Examples:
        query="Python programming" → Returns Python article summary
        query="Albert Einstein" → Returns Einstein biography summary
    """
    try:
        # Get the Wikipedia page
        page = wiki.page(query)
        
        if not page.exists():
            return f"No Wikipedia article found for '{query}'."
        
        # Get the summary (first few paragraphs)
        summary = page.summary[:1000]  # Limit to 1000 chars
        
        return f"Wikipedia: {page.title}\n\n{summary}..."
        
    except Exception as e:
        return f"Error searching Wikipedia for '{query}': {str(e)}"
```

**How it works:**
1. Use `wikipediaapi` library to search
2. Get the article summary
3. Limit length to avoid overwhelming Claude
4. Return formatted text

---

### Tool 4: file_io.py

**File:** `simple/tools/file_io.py`

```python
import os
from pathlib import Path

def file_io(action: str, path: str, content: str = "") -> str:
    """
    Read, write, or append to files.
    
    Actions:
        - "read": Read file contents
        - "write": Write content to file (overwrites)
        - "append": Add content to end of file
    """
    try:
        # Security: Only allow files in current directory
        file_path = Path(path)
        if file_path.is_absolute() or ".." in str(file_path):
            return "Error: Only relative paths in current directory allowed."
        
        if action == "read":
            if not file_path.exists():
                return f"File '{path}' not found."
            return file_path.read_text(encoding='utf-8')
        
        elif action == "write":
            file_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote to '{path}'."
        
        elif action == "append":
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully appended to '{path}'."
        
        else:
            return f"Unknown action: {action}. Use 'read', 'write', or 'append'."
    
    except Exception as e:
        return f"File operation error: {str(e)}"
```

**Security notes:**
- Only allows relative paths (no `/etc/passwd`)
- Blocks `..` path traversal (no `../../sensitive.txt`)
- All operations in current directory only

---

### Tool 5: search.py

**File:** `simple/tools/search.py`

```python
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    No API key needed!
    
    Examples:
        query="Python tutorials" → Returns top 5 web results
        query="weather API" → Returns relevant links
    """
    try:
        # Create DuckDuckGo search client
        ddgs = DDGS()
        
        # Perform search
        results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return f"No results found for '{query}'."
        
        # Format results
        output = f"Web search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['title']}\n"
            output += f"   {result['href']}\n"
            output += f"   {result['body']}\n\n"
        
        return output
        
    except Exception as e:
        return f"Search error: {str(e)}"
```

**How it works:**
1. Use DuckDuckGo search (no API key needed!)
2. Get top N results
3. Format with title, URL, snippet
4. Return as text

---

## Utilities: utils/

### logger.py - Pretty Terminal Output

**File:** `simple/utils/logger.py`

```python
from rich.console import Console
from rich.panel import Panel

console = Console()

def log_step(step: int, max_steps: int):
    """Show current step number"""
    console.print(f"\n[bold]─ Step {step}/{max_steps} ─[/bold]\n")

def log_think(text: str):
    """Show agent's reasoning"""
    console.print(Panel(
        text,
        title="🤔 THINK",
        border_style="blue",
        padding=(1, 2)
    ))

def log_act(tool_name: str, tool_input: dict):
    """Show tool being called"""
    import json
    input_str = json.dumps(tool_input, indent=2)
    console.print(Panel(
        f"[bold]{tool_name}[/bold]\n{input_str}",
        title="🔧 ACT",
        border_style="yellow",
        padding=(1, 2)
    ))

def log_observe(result: str, is_error: bool):
    """Show tool result"""
    style = "red" if is_error else "green"
    title = "❌ ERROR" if is_error else "👁️ OBSERVE"
    console.print(Panel(
        result,
        title=title,
        border_style=style,
        padding=(1, 2)
    ))

def log_finish(text: str):
    """Show final answer"""
    console.print(Panel(
        text,
        title="✅ FINISH",
        border_style="green bold",
        padding=(1, 2)
    ))
```

**What it creates:**
```
─ Step 1/15 ─

╭─ 🤔 THINK ────────────────────────────────────╮
│ I need to check the weather in Tokyo          │
╰───────────────────────────────────────────────╯

╭─ 🔧 ACT ──────────────────────────────────────╮
│ get_weather                                   │
│ {"city": "Tokyo"}                             │
╰───────────────────────────────────────────────╯

╭─ 👁️ OBSERVE ─────────────────────────────────╮
│ Tokyo: 15°C, Cloudy                           │
│ 7-day forecast: ...                           │
╰───────────────────────────────────────────────╯
```

---

### schema.py - Type Safety

**File:** `simple/utils/schema.py`

```python
from pydantic import BaseModel

class ToolCall(BaseModel):
    """Type-safe representation of a tool call"""
    id: str          # "toolu_123abc"
    name: str        # "get_weather"
    input: dict      # {"city": "Tokyo"}
```

**Why Pydantic?**
- Type checking at runtime
- Automatic validation
- Better IDE autocomplete
- Clear data structures

---


## Complete Flow Example

Let's trace a complete execution:

**User:** "What's the weather in Tokyo?"

### Step 1: Initialization

```python
# main.py
run_single("What's the weather in Tokyo?")

# agent/loop.py
def run_agent(task):
    client = anthropic.Anthropic(...)
    memory = ConversationBuffer()
    memory.add_user("What's the weather in Tokyo?")
    tools = get_tool_definitions()
    
    # Memory now:
    # [
    #   {"role": "user", "content": "What's the weather in Tokyo?"}
    # ]
```

### Step 2: First API Call (THINK)

```python
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[
            {"name": "get_weather", "description": "...", ...},
            {"name": "calculator", ...},
            # ... all tools
        ],
        messages=[
            {"role": "user", "content": "What's the weather in Tokyo?"}
        ]
    )
    
    # Claude responds:
    # response.content = [
    #   {
    #     "type": "text",
    #     "text": "I'll check the current weather in Tokyo."
    #   },
    #   {
    #     "type": "tool_use",
    #     "id": "toolu_01A2B3C4D5",
    #     "name": "get_weather",
    #     "input": {"city": "Tokyo"}
    #   }
    # ]
    # response.stop_reason = "tool_use"
```

### Step 3: Save to Memory

```python
    memory.add_assistant(response.content)
    
    # Memory now:
    # [
    #   {"role": "user", "content": "What's the weather in Tokyo?"},
    #   {
    #     "role": "assistant",
    #     "content": [
    #       {"type": "text", "text": "I'll check the current weather..."},
    #       {"type": "tool_use", "id": "toolu_01A2B3C4D5", "name": "get_weather", ...}
    #     ]
    #   }
    # ]
```

### Step 4: Check Stop Reason

```python
    if response.stop_reason == "end_turn":
        # Not this time!
        return final_text
    
    if response.stop_reason == "tool_use":
        # Yes! Claude wants to use a tool
```

### Step 5: Execute Tool (ACT)

```python
        for block in response.content:
            if block.type == "tool_use":
                tool_call = ToolCall(
                    id="toolu_01A2B3C4D5",
                    name="get_weather",
                    input={"city": "Tokyo"}
                )
                
                # Dispatch to tools/registry.py
                result, is_error = dispatch("get_weather", {"city": "Tokyo"})
                
                # tools/registry.py does:
                # fn = TOOL_FUNCTIONS["get_weather"]  # → weather.py:get_weather
                # result = fn(city="Tokyo")
                
                # tools/weather.py does:
                # 1. Geocode Tokyo → lat=35.6762, lon=139.6503
                # 2. Call Open-Meteo API
                # 3. Format result
                
                # result = "Weather in Tokyo:\nCurrent: 15°C, Humidity: 65%\n\n7-day forecast:\n..."
                # is_error = False
```

### Step 6: Save Tool Result (OBSERVE)

```python
                memory.add_tool_result(
                    tool_use_id="toolu_01A2B3C4D5",
                    result="Weather in Tokyo:\nCurrent: 15°C...",
                    is_error=False
                )
                
                # Memory now:
                # [
                #   {"role": "user", "content": "What's the weather in Tokyo?"},
                #   {"role": "assistant", "content": [...]},
                #   {
                #     "role": "user",
                #     "content": [{
                #       "type": "tool_result",
                #       "tool_use_id": "toolu_01A2B3C4D5",
                #       "content": "Weather in Tokyo:\nCurrent: 15°C...",
                #       "is_error": False
                #     }]
                #   }
                # ]
```

### Step 7: Loop Back (Second THINK)

```python
    # Loop continues to step 2
    for step in range(1, MAX_STEPS + 1):  # step = 2
        response = client.messages.create(
            model=...,
            system=...,
            tools=...,
            messages=memory.get_messages()  # All 3 messages above!
        )
        
        # Claude now sees:
        # - Original question
        # - Its previous reasoning + tool call
        # - The tool result
        
        # Claude responds:
        # response.content = [
        #   {
        #     "type": "text",
        #     "text": "Based on the weather data, Tokyo is currently 15°C with 65% humidity. The 7-day forecast shows..."
        #   }
        # ]
        # response.stop_reason = "end_turn"
```

### Step 8: Finish

```python
        if response.stop_reason == "end_turn":
            final_text = _extract_text(response.content)
            # final_text = "Based on the weather data, Tokyo is currently..."
            
            log_finish(final_text)
            return final_text
        
    # Returns to agent/runner.py
    # Which prints to user
```

### Terminal Output

```
─ Step 1/15 ─

╭─ 🤔 THINK ─────────────────────────────────────────────╮
│ I'll check the current weather in Tokyo.               │
╰────────────────────────────────────────────────────────╯

╭─ 🔧 ACT ───────────────────────────────────────────────╮
│ get_weather                                            │
│ {                                                      │
│   "city": "Tokyo"                                      │
│ }                                                      │
╰────────────────────────────────────────────────────────╯

╭─ 👁️ OBSERVE ──────────────────────────────────────────╮
│ Weather in Tokyo:                                      │
│ Current: 15°C, Humidity: 65%                           │
│                                                        │
│ 7-day forecast:                                        │
│ 2026-06-12: 12°C to 18°C                               │
│ 2026-06-13: 14°C to 20°C                               │
│ ...                                                    │
╰────────────────────────────────────────────────────────╯

─ Step 2/15 ─

╭─ 🤔 THINK ─────────────────────────────────────────────╮
│ Based on the weather data, Tokyo is currently 15°C     │
│ with 65% humidity. The forecast shows temperatures     │
│ ranging from 12-20°C over the next week.               │
╰────────────────────────────────────────────────────────╯

╭─ ✅ FINISH ────────────────────────────────────────────╮
│ The weather in Tokyo is currently 15°C with 65%        │
│ humidity. Over the next 7 days, temperatures will      │
│ range from 12°C to 20°C, with the warmest days         │
│ expected on June 13-14.                                │
╰────────────────────────────────────────────────────────╯
```

---

## Key Takeaways

### 1. The Loop is Simple
```python
while not done:
    response = call_claude()
    
    if response.stop_reason == "end_turn":
        return answer
    
    if response.stop_reason == "tool_use":
        result = run_tool()
        memory.add_result(result)
        continue  # Loop back
```

### 2. Memory is Critical
- Claude is stateless
- Every API call needs full conversation history
- Tool results go in memory as "user" messages
- This is how Claude learns from tool outputs

### 3. Tools are Just Functions
- Python function with clear inputs
- Returns a string
- Registered in registry.py
- Claude sees the schema, calls by name

### 4. Stop Reasons Control Flow
- `end_turn` → Done, return answer
- `tool_use` → Run tool, loop
- `max_tokens` → Need more tokens (rare)

### 5. Error Handling Matters
- Tools can fail (network, invalid input)
- `is_error` flag tells Claude something went wrong
- Claude can retry or try different approach

---

## Differences Between Levels

### Simple → Intermediate

**Changes in `agent/loop.py`:**
```python
# NEW: Streaming
def _call_api(...):
    with client.messages.stream(**kwargs) as stream:
        for token in stream.text_stream:
            print(token, end="", flush=True)

# NEW: Retry
def _dispatch_with_retry(tool_name, tool_input):
    for attempt in range(MAX_RETRIES):
        result, is_error = dispatch(...)
        if not is_error:
            return result
    return result  # Give up

# NEW: Token tracking
total_input_tokens += response.usage.input_tokens
total_output_tokens += response.usage.output_tokens
```

### Intermediate → Advanced

**Changes in `agent/loop.py`:**
```python
# NEW: Plan first
if PLAN_FIRST:
    plan = _plan_phase(client, task)
    task = f"{task}\n\n[Your plan]\n{plan}\n\n..."

# NEW: Caching (in tools/registry.py)
cache_key = f"{tool_name}:{json.dumps(tool_input)}"
if cache_key in _cache:
    return _cache[cache_key], False
```

---

## Summary

**You've now learned:**
- ✅ How the ReAct loop works
- ✅ How tools are registered and dispatched
- ✅ How conversation memory is managed
- ✅ How each tool is implemented
- ✅ How terminal output is formatted
- ✅ Complete execution flow from start to finish
- ✅ Differences between Simple/Intermediate/Advanced

**Next steps:**
1. Run the code and watch it execute
2. Add `print()` statements to see values
3. Create your own tool
4. Modify the system prompt
5. Build something useful!

---

**Happy coding!** 🚀

If you understand this, you understand how ALL ReAct agents work. LangChain, AutoGPT, and other frameworks do the same thing—they just add more features on top of this core loop.
