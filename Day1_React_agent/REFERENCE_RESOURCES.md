# AGENTIC AI ENGINEERING BOOTCAMP
# Day 1 — Bare-Metal ReAct Agent
## Reference Resources & Study Guide

*100% laptop-friendly · API-only · No GPU required*

---

## What You Build Today

A production-quality ReAct agent built entirely from scratch — no LangChain, no frameworks. Just the raw Anthropic SDK, a hand-written loop, and your own tool dispatcher.

By end of session you will have:
- A working agent that thinks, acts, observes, and loops autonomously
- Three live tools: web search (DuckDuckGo), Python calculator, file I/O
- A clean conversation memory buffer you control completely
- A coloured terminal UI showing every reasoning step in real time
- Deep understanding of how every framework (LangChain, CrewAI) works under the hood

---

## Session Structure (2 Hours)

- **20 min** → Context: What is a ReAct loop? How does tool-calling work at the API level?
- **100 min** → Build: Implement the full agent from scratch following the code in this repo
- **20 min** → Extend: Add your own 4th tool (suggestions below)

---

## The ReAct Pattern — Core Concept

<cite index="2-5,2-6,2-7">ReAct (Reasoning + Acting) is the foundation of all modern agents. The paper by Yao et al. (2022) showed that interleaving reasoning traces with actions dramatically outperforms either alone.</cite>

```
User Task
 │
 ▼
┌─────────────────────────────────────────┐
│ THINK → What do I need to do next?     │ ← LLM call (claude API)
│ ACT → Call a tool                      │ ← tool_use block
│ OBSERVE → Read the result              │ ← tool_result block
└─────────────────────────────────────────┘
 │
 loop until stop_reason == 'end_turn'
 │
 ▼
Final Answer
```

---

## Key Concepts to Understand

### 1. Tool Definitions

<cite index="2-11,2-12">Tools are described to the LLM as JSON Schema objects. The model decides when and how to call them — you never call tools directly.</cite>

```json
{
  "name": "calculator",
  "description": "Evaluate a math expression safely.",
  "input_schema": {
    "type": "object",
    "properties": {
      "expression": { "type": "string" }
    },
    "required": ["expression"]
  }
}
```

### 2. Stop Reasons

<cite index="2-15,2-16,2-17,2-18,2-19,2-20">
- **end_turn** — the model finished and gave a final answer. Loop stops.
- **tool_use** — the model wants to call one or more tools. Process them and loop.
- **max_tokens** — ran out of tokens mid-response. Handle gracefully.
</cite>

### 3. Conversation History

<cite index="2-22,2-23,2-24">The Anthropic API is stateless. You pass the full conversation every time. Tool results go in user messages — this is the detail most beginners miss.</cite>

```python
messages = [
  { role: 'user', content: 'What is sqrt(144)?' },
  { role: 'assistant', content: [tool_use_block] },
  { role: 'user', content: [tool_result_block] },  # ← tool results here
  { role: 'assistant', content: [text_block] },    # ← final answer
]
```

---

## Official Documentation

### Anthropic SDK & Tool Use

| Resource | Type | Why It Matters |
|----------|------|----------------|
| [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use) | Docs | The definitive guide to tool calling — read this first |
| [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) | GitHub | Source code for the SDK you are using today |
| [Messages API Reference](https://docs.anthropic.com/claude/reference/messages_post) | API Ref | Full parameter reference for client.messages.create() |
| [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) | Docs | How to write effective system prompts for agents |
| [Model Comparison](https://docs.anthropic.com/claude/docs/models-overview) | Docs | Choose the right Claude model for cost vs capability |

---

## Foundational Research Papers

<cite index="2-27,2-28">These are the papers that define the field. You don't need to read them fully today — bookmark them and return after Week 1.</cite>

| Resource | Type | Why It Matters |
|----------|------|----------------|
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | Paper | The original ReAct paper (Yao et al., 2022) — foundation of everything you build today |
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) | Paper | How LLMs learn to use tools via self-supervised training |
| [Chain-of-Thought Prompting Elicits Reasoning in LLMs](https://arxiv.org/abs/2201.11903) | Paper | Wei et al. — why step-by-step reasoning works |
| [HuggingGPT: Solving AI Tasks with ChatGPT](https://arxiv.org/abs/2303.17580) | Paper | LLM as a controller orchestrating specialised models |
| [Agents: An Overview](https://lilianweng.github.io/posts/2023-06-23-agent/) | Blog | Lilian Weng's landmark overview of LLM agents — essential reading |
| [Tree of Thoughts](https://arxiv.org/abs/2305.10601) | Paper | Deliberate reasoning beyond linear chain-of-thought |

---

## Libraries Used Today

| Resource | Type | Why It Matters |
|----------|------|----------------|
| [anthropic (PyPI)](https://pypi.org/project/anthropic/) | PyPI | Official Python SDK — pip install anthropic |
| [duckduckgo-search](https://github.com/deedy5/duckduckgo_search) | GitHub | No API key needed for web search — perfect for local dev |
| [pydantic v2](https://docs.pydantic.dev/) | Docs | Data validation for tool inputs and outputs |
| [rich](https://rich.readthedocs.io/) | Docs | Beautiful terminal output — powers the THINK/ACT/OBSERVE panels |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | PyPI | Loads .env files — keeps API keys out of code |

---

## Extension Challenges

Finish early? Push the agent further with these additions:

### Beginner
- Add a weather tool using the Open-Meteo API (free, no key needed)
- Add a Wikipedia tool using the wikipedia-api Python package
- Increase MAX_STEPS and give the agent a longer research task

### Intermediate
- Add streaming output so you see tokens appear in real time (use `client.messages.stream()`)
- Add a retry mechanism — if a tool fails, the agent retries with a modified input
- Build a token usage tracker — show cost per run using the usage object in the response

### Advanced
- Implement a 'plan first' step — force the agent to output a numbered plan before acting
- Add tool result caching — if the same tool is called twice with the same args, return the cached result
- Build an eval harness: 5 tasks, run agent on each, score pass/fail, log accuracy

---

## Further Learning — Courses & Tutorials

| Resource | Type | Why It Matters |
|----------|------|----------------|
| [DeepLearning.AI: Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) | Course | Free short course — perfect companion for this week |
| [DeepLearning.AI: AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) | Course | Free — directly relevant to Week 2 of this bootcamp |
| [Anthropic Courses on GitHub](https://github.com/anthropics/courses) | GitHub | Official notebooks and tutorials from Anthropic |
| [Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) | GitHub | Hands-on exercises for effective Claude prompting |
| [Full Stack Deep Learning](https://fullstackdeeplearning.com/) | Course | Production ML systems — relevant from Week 3 onward |

---

## Communities & Stay Current

| Resource | Type | Why It Matters |
|----------|------|----------------|
| [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) | Reddit | Most active community for LLM engineering discussions |
| [Latent Space Discord](https://discord.gg/latentspace) | Discord | AI engineers — great for agentic AI topics |
| [LangChain Discord](https://discord.gg/langchain) | Discord | Framework updates, community projects, help |
| [Hugging Face Daily Papers](https://huggingface.co/papers) | Feed | Daily ML papers — stay current with the field |
| [The Batch (Andrew Ng)](https://www.deeplearning.ai/the-batch/) | Newsletter | Weekly digest of the most important AI developments |
| [Ahead of AI (Sebastian Raschka)](https://magazine.sebastianraschka.com/) | Newsletter | Deep technical ML newsletter — highly recommended |

---

## Quick Glossary

<cite index="2-33,2-34">**ReAct** — Reasoning + Acting. Agent loop pattern: think → act → observe → repeat.</cite>

<cite index="2-35">**Tool Call** — A structured request from the LLM to invoke a function you provide.</cite>

<cite index="2-36">**Tool Result** — The output of your function, passed back to the LLM as context.</cite>

<cite index="2-37">**Stop Reason** — Why the API returned: end_turn (finished) or tool_use (wants a tool).</cite>

<cite index="2-38">**System Prompt** — Instructions that define the agent's persona, rules, and constraints.</cite>

<cite index="2-39">**Context Window** — The maximum tokens the model can process in one call (200K for Claude Sonnet).</cite>

<cite index="2-40">**Agentic Loop** — The iterative cycle where the model drives its own next steps.</cite>

---

*Agentic AI Engineering Bootcamp · Day 1 of 30 · Build something every day*
