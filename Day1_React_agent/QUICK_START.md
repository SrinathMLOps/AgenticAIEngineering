# ⚡ Quick Start Guide

## 🎯 30-Second Setup

```bash
# 1. Choose a level
cd simple

# 2. Setup environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 3. Install
pip install -r requirements.txt

# 4. Configure
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux

# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# 5. Run!
python main.py
```

---

## 🗺️ Visual Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         USER TASK                             │
│        "What's the weather in Tokyo and save it?"            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   STEP 1: THINK        │
            │   (Claude API Call)    │
            │ "I need Tokyo weather" │
            └────────────┬───────────┘
                         │
                 stop_reason = "tool_use"
                         │
                         ▼
            ┌────────────────────────┐
            │   STEP 1: ACT          │
            │   get_weather("Tokyo") │
            │                        │
            └────────────┬───────────┘
                         │
                         ▼
            ┌─────────────────────────────────┐
            │   STEP 1: OBSERVE               │
            │   Result: "Tokyo: 15°C, Cloudy" │
            │   (added to memory)             │
            └────────────┬────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   STEP 2: THINK        │
            │   (Claude API Call)    │
            │ "Now I'll save it"     │
            └────────────┬───────────┘
                         │
                 stop_reason = "tool_use"
                         │
                         ▼
            ┌──────────────────────────────────┐
            │   STEP 2: ACT                    │
            │   file_io(action="write",        │
            │           path="tokyo.txt",      │
            │           content="Tokyo: 15°C") │
            └────────────┬─────────────────────┘
                         │
                         ▼
            ┌─────────────────────────────────────┐
            │   STEP 2: OBSERVE                   │
            │   "Successfully wrote to tokyo.txt" │
            │   (added to memory)                 │
            └────────────┬────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   STEP 3: THINK        │
            │   (Claude API Call)    │
            │ "Task complete!"       │
            └────────────┬───────────┘
                         │
                 stop_reason = "end_turn"
                         │
                         ▼
            ┌──────────────────────────────────────┐
            │   ✅ FINISH                          │
            │   "I've saved Tokyo's weather        │
            │    to tokyo.txt. It's 15°C..."      │
            └──────────────────────────────────────┘
```

---

## 📂 Three Levels Comparison

| Feature | Simple | Intermediate | Advanced |
|---------|--------|--------------|----------|
| ReAct Loop | ✅ | ✅ | ✅ |
| 5 Tools | ✅ | ✅ | ✅ |
| Streaming Output | ❌ | ✅ | ✅ |
| Auto Retry | ❌ | ✅ | ✅ |
| Token Tracking | ❌ | ✅ | ✅ |
| Plan-First | ❌ | ❌ | ✅ |
| Tool Caching | ❌ | ❌ | ✅ |
| Eval Harness | ❌ | ❌ | ✅ |

---

## 🎯 Try These First

### Simple Tasks (1 minute each)
```bash
"What is the weather in London?"
"Calculate 123 * 456"
"Look up Python on Wikipedia"
```

### Medium Tasks (2-3 minutes)
```bash
"Search for top Python frameworks and save to file"
"Get weather for Tokyo and explain what to wear"
"Who invented JavaScript? Save the answer."
```

### Complex Tasks (5+ minutes)
```bash
"Research the history of AI: key milestones, people, and current state. Save a report."
"Compare Python vs JavaScript: look up both on Wikipedia, search for popularity stats, and save a comparison."
```

---

## 🔑 Key Files to Read

**Start Here:**
1. `agent/loop.py` - The ReAct loop (100 lines)
2. `tools/weather.py` - Example tool (30 lines)
3. `tools/registry.py` - Tool dispatch (50 lines)

**Then:**
4. `memory/buffer.py` - Conversation history
5. `utils/logger.py` - Pretty terminal output

**Total reading time:** ~30 minutes to understand the core!

---

## 💡 Quick Tips

1. **Always start with Simple** - It has the cleanest code
2. **Read the code comments** - They explain everything
3. **Break things** - Best way to learn!
4. **Check .env settings** - Toggle features on/off
5. **Use the logger output** - Shows you what's happening

---

## 🐛 Common Issues

**"No module named 'anthropic'"**
→ Run: `pip install -r requirements.txt`

**"Invalid API key"**
→ Get key at: https://console.anthropic.com/
→ Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

**"Agent reached max steps"**
→ Increase in `.env`: `MAX_STEPS=25`

---

## 🎓 Learning Path

```
Week 1: Simple
├─ Day 1: Run examples, understand output
├─ Day 2: Read agent/loop.py line by line
├─ Day 3: Study tools/weather.py, create your own tool
└─ Day 4: Modify system prompt, experiment

Week 2: Intermediate
├─ Day 5: Compare with Simple, find differences
├─ Day 6: Toggle streaming on/off, observe
└─ Day 7: Study retry logic, test error handling

Week 3: Advanced
├─ Day 8: Understand plan-first approach
├─ Day 9: Study tool caching mechanism
└─ Day 10: Run eval_harness, create your own eval

Beyond:
├─ Build custom tools
├─ Create specialized agents
└─ Deploy your own project!
```

---

## 📚 Next Steps

After mastering this:
1. Read [BEGINNERS_GUIDE.md](./BEGINNERS_GUIDE.md) for deep dive
2. Study the official [Anthropic Tool Use docs](https://docs.anthropic.com/claude/docs/tool-use)
3. Explore [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
4. Build your own agent for a real task!

---

**Ready to start?**

```bash
cd simple
python main.py
```

**First task to try:**
```
"What's the weather in your favorite city?"
```

Let's go! 🚀
