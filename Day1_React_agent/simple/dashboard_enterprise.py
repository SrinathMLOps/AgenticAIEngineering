"""
Enterprise ReAct Agent Dashboard
=================================
Professional web interface for AI agent execution monitoring and analysis.

Features:
- Real-time agent execution tracking
- Detailed step-by-step analysis
- Performance metrics and cost analysis
- Export capabilities
- Enterprise-grade UI design

Run: python dashboard_enterprise.py
Access: http://localhost:7860
"""
import os
import json
from datetime import datetime
import gradio as gr
from dotenv import load_dotenv
from agent.loop import run_agent
from memory.buffer import ConversationBuffer
from tools.registry import get_tool_definitions
import anthropic

load_dotenv()


class EnterpriseAgentDashboard:
    """Enterprise-grade agent execution monitoring system"""
    
    def __init__(self):
        self.execution_history = []
        self.current_execution = None
        
    def execute_task(self, task: str):
        """Execute agent task with comprehensive logging and metrics"""
        if not task or not task.strip():
            return self._format_error("Task input is required. Please provide a valid task description.")
        
        # Initialize execution metadata
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_execution = {
            "id": execution_id,
            "task": task,
            "start_time": datetime.now(),
            "steps": [],
            "metrics": {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "execution_time": 0.0
            }
        }
        
        try:
            # Initialize AI client and components
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            memory = ConversationBuffer()
            memory.add_user(task)
            tools = get_tool_definitions()
            
            MODEL = os.getenv("MODEL", "claude-sonnet-4-20250514")
            MAX_STEPS = int(os.getenv("MAX_STEPS", "15"))
            
            SYSTEM_PROMPT = """You are an enterprise AI agent designed for professional task execution.

Available tools: web_search, calculator, file_io, get_weather, wikipedia_search.

Execution Guidelines:
- Analyze tasks systematically before taking action
- Utilize tools efficiently and only when necessary
- Provide comprehensive analysis of tool results
- Deliver complete, accurate final responses
- Handle errors gracefully and attempt alternative approaches

Quality Standards:
- Verify all calculations and data
- Cross-reference information when possible
- Document decision-making process
- Maintain professional communication standards
"""
            
            # Execute agent loop
            for step_number in range(1, MAX_STEPS + 1):
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=memory.get_messages(),
                )
                
                memory.add_assistant(response.content)
                
                # Record step metrics
                step_data = {
                    "step_number": step_number,
                    "timestamp": datetime.now().isoformat(),
                    "stop_reason": response.stop_reason,
                    "actions": [],
                    "tokens": {
                        "input": response.usage.input_tokens,
                        "output": response.usage.output_tokens
                    }
                }
                
                # Update metrics
                self.current_execution["metrics"]["total_input_tokens"] += response.usage.input_tokens
                self.current_execution["metrics"]["total_output_tokens"] += response.usage.output_tokens
                
                # Process response based on stop reason
                if response.stop_reason == "end_turn":
                    final_text = self._extract_text_content(response.content)
                    step_data["actions"].append({
                        "type": "completion",
                        "content": final_text
                    })
                    self.current_execution["steps"].append(step_data)
                    break
                
                if response.stop_reason == "tool_use":
                    for block in response.content:
                        if block.type == "text" and block.text:
                            step_data["actions"].append({
                                "type": "analysis",
                                "content": block.text
                            })
                        
                        if block.type == "tool_use":
                            from tools.registry import dispatch
                            
                            step_data["actions"].append({
                                "type": "tool_invocation",
                                "tool_name": block.name,
                                "parameters": block.input
                            })
                            
                            # Execute tool
                            result, is_error = dispatch(block.name, block.input)
                            
                            step_data["actions"].append({
                                "type": "tool_result",
                                "result": result,
                                "status": "error" if is_error else "success"
                            })
                            
                            memory.add_tool_result(block.id, result, is_error)
                    
                    self.current_execution["steps"].append(step_data)
                    continue
                
                # Unexpected stop reason
                step_data["actions"].append({
                    "type": "error",
                    "content": f"Unexpected stop reason: {response.stop_reason}"
                })
                self.current_execution["steps"].append(step_data)
                break
            
            # Calculate final metrics
            end_time = datetime.now()
            self.current_execution["end_time"] = end_time
            self.current_execution["metrics"]["execution_time"] = (
                end_time - self.current_execution["start_time"]
            ).total_seconds()
            
            # Calculate cost (Claude Sonnet 4.5 pricing)
            input_cost = self.current_execution["metrics"]["total_input_tokens"] / 1_000_000 * 3.0
            output_cost = self.current_execution["metrics"]["total_output_tokens"] / 1_000_000 * 15.0
            self.current_execution["metrics"]["total_cost"] = input_cost + output_cost
            
            # Add to history
            self.execution_history.append(self.current_execution)
            
            return self._format_execution_report()
            
        except anthropic.AuthenticationError:
            return self._format_error("Authentication failed. Please verify your API key configuration.")
        except Exception as e:
            return self._format_error(f"Execution error: {str(e)}")
    
    def _extract_text_content(self, content):
        """Extract text from content blocks"""
        parts = [block.text for block in content if hasattr(block, "text") and block.text]
        return "\n".join(parts) if parts else "No response content."
    
    def _format_execution_report(self):
        """Generate comprehensive HTML report for execution"""
        exec_data = self.current_execution
        
        html = """
        <div style='font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 1400px; background: #ffffff; color: #1a1a1a;'>
        """
        
        # Header
        html += """
        <div style='background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                    color: white; padding: 30px; border-radius: 2px; margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h1 style='margin: 0 0 10px 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px;'>
                Agent Execution Report
            </h1>
            <p style='margin: 0; opacity: 0.9; font-size: 14px;'>
                Real-time analysis and performance metrics
            </p>
        </div>
        """
        
        # Executive Summary
        metrics = exec_data["metrics"]
        html += f"""
        <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 2px; 
                    padding: 25px; margin-bottom: 30px;'>
            <h2 style='margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #1e293b;'>
                Executive Summary
            </h2>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                        gap: 20px;'>
                <div style='background: white; padding: 20px; border-radius: 2px; 
                            border-left: 3px solid #3b82f6;'>
                    <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                        {len(exec_data["steps"])}
                    </div>
                    <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                                letter-spacing: 0.5px;'>
                        Total Steps
                    </div>
                </div>
                <div style='background: white; padding: 20px; border-radius: 2px; 
                            border-left: 3px solid #8b5cf6;'>
                    <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                        {metrics["total_input_tokens"]:,}
                    </div>
                    <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                                letter-spacing: 0.5px;'>
                        Input Tokens
                    </div>
                </div>
                <div style='background: white; padding: 20px; border-radius: 2px; 
                            border-left: 3px solid #ec4899;'>
                    <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                        {metrics["total_output_tokens"]:,}
                    </div>
                    <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                                letter-spacing: 0.5px;'>
                        Output Tokens
                    </div>
                </div>
                <div style='background: white; padding: 20px; border-radius: 2px; 
                            border-left: 3px solid #10b981;'>
                    <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                        ${metrics["total_cost"]:.4f}
                    </div>
                    <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                                letter-spacing: 0.5px;'>
                        Total Cost USD
                    </div>
                </div>
                <div style='background: white; padding: 20px; border-radius: 2px; 
                            border-left: 3px solid #f59e0b;'>
                    <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                        {metrics["execution_time"]:.2f}s
                    </div>
                    <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                                letter-spacing: 0.5px;'>
                        Execution Time
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Task Information
        html += f"""
        <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                    padding: 25px; margin-bottom: 30px;'>
            <h3 style='margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #1e293b;'>
                Task Description
            </h3>
            <p style='margin: 0; font-size: 14px; line-height: 1.6; color: #475569;'>
                {exec_data["task"]}
            </p>
        </div>
        """
        
        # Execution Steps
        html += """
        <div style='margin-bottom: 30px;'>
            <h2 style='margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #1e293b;'>
                Detailed Execution Log
            </h2>
        """
        
        for step in exec_data["steps"]:
            html += f"""
            <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                        margin-bottom: 20px; overflow: hidden;'>
                <div style='background: #f1f5f9; padding: 15px 25px; 
                            border-bottom: 1px solid #e2e8f0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h3 style='margin: 0; font-size: 15px; font-weight: 600; color: #1e293b;'>
                            Step {step["step_number"]} of {len(exec_data["steps"])}
                        </h3>
                        <span style='font-size: 12px; color: #64748b;'>
                            {step["tokens"]["input"]} input | {step["tokens"]["output"]} output tokens
                        </span>
                    </div>
                </div>
                <div style='padding: 25px;'>
            """
            
            for action in step["actions"]:
                if action["type"] == "analysis":
                    html += f"""
                    <div style='background: #eff6ff; border-left: 3px solid #3b82f6; 
                                padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                        <div style='font-size: 12px; font-weight: 600; color: #1e40af; 
                                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                            Analysis
                        </div>
                        <div style='font-size: 14px; color: #1e3a8a; line-height: 1.6; 
                                    white-space: pre-wrap;'>
                            {action["content"]}
                        </div>
                    </div>
                    """
                
                elif action["type"] == "tool_invocation":
                    params_json = json.dumps(action["parameters"], indent=2)
                    html += f"""
                    <div style='background: #fff7ed; border-left: 3px solid #f59e0b; 
                                padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                        <div style='font-size: 12px; font-weight: 600; color: #b45309; 
                                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                            Tool Invocation: {action["tool_name"]}
                        </div>
                        <pre style='background: #fefce8; padding: 12px; border-radius: 2px; 
                                    margin: 0; overflow-x: auto; font-size: 13px; color: #854d0e; 
                                    border: 1px solid #fef08a;'>{params_json}</pre>
                    </div>
                    """
                
                elif action["type"] == "tool_result":
                    if action["status"] == "success":
                        bg_color = "#f0fdf4"
                        border_color = "#10b981"
                        text_color = "#065f46"
                        title_color = "#047857"
                        status_label = "Success"
                    else:
                        bg_color = "#fef2f2"
                        border_color = "#ef4444"
                        text_color = "#991b1b"
                        title_color = "#dc2626"
                        status_label = "Error"
                    
                    html += f"""
                    <div style='background: {bg_color}; border-left: 3px solid {border_color}; 
                                padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                        <div style='font-size: 12px; font-weight: 600; color: {title_color}; 
                                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                            Tool Result: {status_label}
                        </div>
                        <div style='font-size: 14px; color: {text_color}; line-height: 1.6; 
                                    white-space: pre-wrap; max-height: 300px; overflow-y: auto;'>
                            {action["result"]}
                        </div>
                    </div>
                    """
                
                elif action["type"] == "completion":
                    html += f"""
                    <div style='background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                                border-radius: 2px; padding: 20px; color: white;'>
                        <div style='font-size: 14px; font-weight: 600; text-transform: uppercase; 
                                    letter-spacing: 0.5px; margin-bottom: 15px;'>
                            Final Response
                        </div>
                        <div style='font-size: 15px; line-height: 1.7; white-space: pre-wrap;'>
                            {action["content"]}
                        </div>
                    </div>
                    """
                
                elif action["type"] == "error":
                    html += f"""
                    <div style='background: #fef2f2; border: 1px solid #fecaca; 
                                padding: 15px; border-radius: 2px;'>
                        <div style='font-size: 12px; font-weight: 600; color: #dc2626; 
                                    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                            Execution Error
                        </div>
                        <div style='font-size: 14px; color: #991b1b;'>
                            {action["content"]}
                        </div>
                    </div>
                    """
            
            html += """
                </div>
            </div>
            """
        
        html += "</div></div>"
        return html
    
    def _format_error(self, error_message):
        """Format error message for display"""
        return f"""
        <div style='font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 800px;'>
            <div style='background: #fef2f2; border: 1px solid #fecaca; border-radius: 2px; 
                        padding: 25px;'>
                <h3 style='margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #dc2626;'>
                    Execution Error
                </h3>
                <p style='margin: 0 0 15px 0; font-size: 14px; color: #991b1b; line-height: 1.6;'>
                    {error_message}
                </p>
                <div style='background: white; border: 1px solid #fecaca; border-radius: 2px; 
                            padding: 15px; margin-top: 15px;'>
                    <p style='margin: 0; font-size: 13px; color: #475569;'>
                        <strong>Troubleshooting:</strong>
                    </p>
                    <ul style='margin: 10px 0 0 0; padding-left: 20px; font-size: 13px; 
                                color: #475569; line-height: 1.6;'>
                        <li>Verify API key configuration in .env file</li>
                        <li>Check network connectivity</li>
                        <li>Review input parameters and format</li>
                        <li>Consult system logs for detailed error information</li>
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def export_execution_log(self):
        """Export current execution as JSON"""
        if not self.current_execution:
            return "No execution data available for export."
        
        try:
            export_data = {
                "execution_id": self.current_execution["id"],
                "task": self.current_execution["task"],
                "start_time": self.current_execution["start_time"].isoformat(),
                "end_time": self.current_execution["end_time"].isoformat(),
                "metrics": self.current_execution["metrics"],
                "steps": self.current_execution["steps"]
            }
            
            filename = f"execution_log_{self.current_execution['id']}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return f"Execution log exported successfully to: {filename}"
        except Exception as e:
            return f"Export failed: {str(e)}"


# Initialize dashboard
dashboard = EnterpriseAgentDashboard()


def process_task(task):
    """Process task and return formatted report"""
    return dashboard.execute_task(task)


def export_log():
    """Export execution log"""
    return dashboard.export_execution_log()


# Build Gradio Interface
with gr.Blocks(
    title="Enterprise AI Agent Dashboard",
    theme=gr.themes.Default(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate"
    ),
    css="""
    .gradio-container {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif !important;
    }
    """
) as demo:
    
    gr.Markdown("""
    # Enterprise AI Agent Dashboard
    
    **Advanced AI Agent Execution Monitoring and Analysis Platform**
    
    This enterprise-grade dashboard provides comprehensive visibility into AI agent operations, 
    including real-time execution tracking, performance metrics, cost analysis, and detailed logging.
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            task_input = gr.Textbox(
                label="Task Description",
                placeholder="Enter detailed task requirements for agent execution...",
                lines=4,
                info="Provide clear, specific instructions for optimal results"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("""
            ### Example Tasks
            
            **Analysis:**
            - Calculate compound interest on investment portfolio
            - Analyze weather patterns across multiple cities
            
            **Research:**
            - Research company history and founders
            - Compare technical specifications
            
            **Operations:**
            - Generate reports with calculations
            - Process and save data files
            """)
    
    with gr.Row():
        execute_btn = gr.Button("Execute Task", variant="primary", size="lg")
        clear_btn = gr.Button("Clear", size="lg")
        export_btn = gr.Button("Export Log", size="lg", variant="secondary")
    
    output_display = gr.HTML(label="Execution Report")
    export_status = gr.Textbox(label="Export Status", visible=False)
    
    # Example tasks
    gr.Examples(
        examples=[
            ["Calculate the compound interest on $10,000 at 5% annual rate for 10 years. Show year-by-year breakdown."],
            ["Compare the current weather conditions in London, New York, and Tokyo. Provide temperature and conditions for each."],
            ["Research the history of Python programming language using Wikipedia. Include creation date, creator, and key milestones."],
            ["Calculate the square root of 2,048 and multiply the result by 15. Save the final answer to a file named calculation_result.txt."],
        ],
        inputs=task_input,
        label="Example Task Templates"
    )
    
    # Event handlers
    execute_btn.click(
        fn=process_task,
        inputs=task_input,
        outputs=output_display
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        outputs=[task_input, output_display]
    )
    
    export_btn.click(
        fn=export_log,
        outputs=export_status
    ).then(
        fn=lambda x: gr.update(visible=True),
        inputs=export_status,
        outputs=export_status
    )
    
    gr.Markdown("""
    ---
    
    ### Dashboard Features
    
    **Real-time Monitoring**
    - Step-by-step execution tracking
    - Performance metrics and analytics
    - Cost monitoring and optimization
    
    **Analysis Components**
    - Agent reasoning and decision-making
    - Tool invocation and parameters
    - Result validation and error handling
    - Final response generation
    
    **Export Capabilities**
    - JSON format execution logs
    - Complete audit trail
    - Integration-ready data format
    
    ---
    
    **Technology Stack:** Anthropic Claude API | Gradio | Python  
    **Version:** 1.0 Enterprise Edition
    """)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Enterprise AI Agent Dashboard")
    print("="*70)
    print("\nDashboard URL: http://localhost:7860")
    print("Environment: Production")
    print("API Configuration: Loaded from .env")
    print("\n" + "="*70 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )
