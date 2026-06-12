"""
Gradio Dashboard for ReAct Agent
==================================
Beautiful web interface to showcase the agent's thinking process in real-time.

Run: python dashboard.py
Then open: http://localhost:7860
"""
import os
import gradio as gr
from dotenv import load_dotenv
from agent.loop import run_agent
from memory.buffer import ConversationBuffer
from tools.registry import get_tool_definitions
import anthropic

load_dotenv()

# Track agent steps for display
class DashboardAgent:
    def __init__(self):
        self.steps = []
        self.current_step = 0
    
    def run_with_logging(self, task: str):
        """Run agent and capture all steps for dashboard display"""
        self.steps = []
        self.current_step = 0
        
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        memory = ConversationBuffer()
        memory.add_user(task)
        tools = get_tool_definitions()
        
        MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
        MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))
        
        SYSTEM_PROMPT = """You are a capable AI agent that solves tasks step by step.

You have access to tools: web_search, calculator, file_io, get_weather, wikipedia_search.

## How to behave
- Think carefully before acting. Use tools only when needed.
- After each tool result, reflect on what you learned before deciding the next step.
- When you have enough information, respond with your final answer directly (no tool call).
- Be concise in your reasoning. Prioritise accuracy over speed.
- If a tool fails, try a different approach — don't give up immediately.

## Important
- Never make up facts. If you don't know something, search or look it up.
- Always verify calculations with the calculator tool.
- Save important results to a file if the user might want to keep them.
"""
        
        for step in range(1, MAX_STEPS + 1):
            self.current_step = step
            
            # Call API
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=memory.get_messages(),
            )
            
            memory.add_assistant(response.content)
            
            # Log step
            step_info = {
                "step": step,
                "stop_reason": response.stop_reason,
                "content": [],
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
            # Process response
            if response.stop_reason == "end_turn":
                # Extract final answer
                final_text = self._extract_text(response.content)
                step_info["content"].append({
                    "type": "finish",
                    "text": final_text
                })
                self.steps.append(step_info)
                return self._format_output()
            
            if response.stop_reason == "tool_use":
                # Process thinking and tool calls
                for block in response.content:
                    if block.type == "text" and block.text:
                        step_info["content"].append({
                            "type": "think",
                            "text": block.text
                        })
                    
                    if block.type == "tool_use":
                        # Import dispatch here to avoid circular imports
                        from tools.registry import dispatch
                        
                        step_info["content"].append({
                            "type": "act",
                            "tool": block.name,
                            "input": block.input
                        })
                        
                        # Execute tool
                        result, is_error = dispatch(block.name, block.input)
                        
                        step_info["content"].append({
                            "type": "observe",
                            "result": result,
                            "is_error": is_error
                        })
                        
                        memory.add_tool_result(block.id, result, is_error)
                
                self.steps.append(step_info)
                continue
        
        # Max steps reached
        return self._format_output(max_steps_reached=True)
    
    def _extract_text(self, content):
        """Extract text from content blocks"""
        parts = [block.text for block in content if hasattr(block, "text") and block.text]
        return "\n".join(parts) if parts else "No text response."
    
    def _format_output(self, max_steps_reached=False):
        """Format all steps into beautiful HTML for Gradio"""
        html = "<div style='font-family: system-ui; max-width: 1200px;'>"
        
        # Summary at top
        total_steps = len(self.steps)
        total_input_tokens = sum(s["tokens"]["input"] for s in self.steps)
        total_output_tokens = sum(s["tokens"]["output"] for s in self.steps)
        total_cost = (total_input_tokens / 1_000_000 * 3) + (total_output_tokens / 1_000_000 * 15)
        
        html += f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='margin: 0 0 10px 0;'>🤖 Agent Execution Summary</h2>
            <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;'>
                <div>
                    <div style='font-size: 24px; font-weight: bold;'>{total_steps}</div>
                    <div style='opacity: 0.9;'>Steps</div>
                </div>
                <div>
                    <div style='font-size: 24px; font-weight: bold;'>{total_input_tokens:,}</div>
                    <div style='opacity: 0.9;'>Input Tokens</div>
                </div>
                <div>
                    <div style='font-size: 24px; font-weight: bold;'>{total_output_tokens:,}</div>
                    <div style='opacity: 0.9;'>Output Tokens</div>
                </div>
                <div>
                    <div style='font-size: 24px; font-weight: bold;'>${total_cost:.4f}</div>
                    <div style='opacity: 0.9;'>Cost (USD)</div>
                </div>
            </div>
        </div>
        """
        
        # Each step
        for step_data in self.steps:
            html += f"""
            <div style='border-left: 4px solid #667eea; padding-left: 20px; margin-bottom: 30px;'>
                <h3 style='color: #667eea; margin: 0 0 15px 0;'>
                    Step {step_data['step']}/{len(self.steps)}
                    <span style='float: right; font-size: 14px; color: #666;'>
                        {step_data['tokens']['input']}↓ {step_data['tokens']['output']}↑ tokens
                    </span>
                </h3>
            """
            
            for item in step_data["content"]:
                if item["type"] == "think":
                    html += f"""
                    <div style='background: #f0f7ff; border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                        <div style='color: #2563eb; font-weight: 600; margin-bottom: 8px;'>
                            🤔 THINK
                        </div>
                        <div style='color: #1e40af; white-space: pre-wrap;'>{item['text']}</div>
                    </div>
                    """
                
                elif item["type"] == "act":
                    import json
                    input_formatted = json.dumps(item["input"], indent=2)
                    html += f"""
                    <div style='background: #fff7ed; border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                        <div style='color: #ea580c; font-weight: 600; margin-bottom: 8px;'>
                            🔧 ACT: {item['tool']}
                        </div>
                        <pre style='background: #fff; padding: 10px; border-radius: 4px; 
                                    margin: 0; overflow-x: auto; color: #9a3412;'>{input_formatted}</pre>
                    </div>
                    """
                
                elif item["type"] == "observe":
                    bg_color = "#fef2f2" if item["is_error"] else "#f0fdf4"
                    text_color = "#dc2626" if item["is_error"] else "#16a34a"
                    icon = "❌" if item["is_error"] else "👁️"
                    title = "ERROR" if item["is_error"] else "OBSERVE"
                    
                    html += f"""
                    <div style='background: {bg_color}; border-radius: 8px; padding: 15px; margin-bottom: 10px;'>
                        <div style='color: {text_color}; font-weight: 600; margin-bottom: 8px;'>
                            {icon} {title}
                        </div>
                        <div style='color: {text_color}; white-space: pre-wrap; 
                                    max-height: 300px; overflow-y: auto;'>{item['result']}</div>
                    </div>
                    """
                
                elif item["type"] == "finish":
                    html += f"""
                    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                                border-radius: 8px; padding: 20px; color: white;'>
                        <div style='font-weight: 600; font-size: 18px; margin-bottom: 10px;'>
                            ✅ FINAL ANSWER
                        </div>
                        <div style='font-size: 16px; line-height: 1.6; white-space: pre-wrap;'>{item['text']}</div>
                    </div>
                    """
            
            html += "</div>"
        
        if max_steps_reached:
            html += """
            <div style='background: #fef2f2; border-radius: 8px; padding: 15px; color: #dc2626;'>
                ⚠️ Agent reached maximum steps without completing the task.
            </div>
            """
        
        html += "</div>"
        return html


# Global agent instance
dashboard_agent = DashboardAgent()


def process_query(task, history):
    """Process user query and return formatted output"""
    if not task.strip():
        return "Please enter a task for the agent to solve."
    
    try:
        result_html = dashboard_agent.run_with_logging(task)
        return result_html
    except Exception as e:
        return f"""
        <div style='background: #fef2f2; border-radius: 8px; padding: 20px; color: #dc2626;'>
            <h3>❌ Error</h3>
            <p>{str(e)}</p>
            <p style='font-size: 12px; opacity: 0.8;'>
                Make sure your ANTHROPIC_API_KEY is set in the .env file.
            </p>
        </div>
        """


# Build Gradio Interface
with gr.Blocks(title="ReAct Agent Dashboard", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 ReAct Agent Dashboard
    
    Watch your AI agent think, act, and solve problems step-by-step in real-time.
    
    **Try these examples:**
    - "What is 25 * 47 + 183?"
    - "Search for the latest news about AI agents"
    - "What's the weather in London today?"
    - "Who invented Python? Look it up and save the answer to a file"
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            task_input = gr.Textbox(
                label="Enter your task",
                placeholder="What would you like the agent to do?",
                lines=3
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Run Agent", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear", size="lg")
    
    output_display = gr.HTML(label="Agent Execution")
    
    # Examples
    gr.Examples(
        examples=[
            ["Calculate 15 * 23 + 67"],
            ["Search the web for 'ReAct agents explained'"],
            ["What is the square root of 144? Calculate it."],
            ["Look up 'Claude AI' on the web and summarize it"],
        ],
        inputs=task_input,
    )
    
    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[task_input, gr.State([])],
        outputs=output_display
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        outputs=[task_input, output_display]
    )
    
    gr.Markdown("""
    ---
    
    ### 📊 What You're Seeing:
    
    - **🤔 THINK**: The agent's reasoning about what to do next
    - **🔧 ACT**: Tool calls the agent makes (calculator, search, file operations)
    - **👁️ OBSERVE**: Results returned from tools
    - **✅ FINAL ANSWER**: The agent's complete response
    
    ### 💡 Tips:
    
    - Give clear, specific tasks for best results
    - Watch how the agent breaks down complex problems
    - See token usage and cost for each step
    - The agent can use multiple tools in sequence
    
    **Built with:** Anthropic Claude API · Gradio · Python
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting ReAct Agent Dashboard...")
    print("="*60)
    print("\n📱 Open your browser and go to: http://localhost:7860")
    print("🔑 Make sure ANTHROPIC_API_KEY is set in your .env file")
    print("\n" + "="*60 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True to create a public link
        show_error=True
    )
