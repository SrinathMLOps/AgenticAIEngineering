"""
╔══════════════════════════════════════════════════════════════════╗
║  PROFESSIONAL ENTERPRISE MULTI-AGENT DASHBOARD                   ║
║  Corporate-Grade UI with Agentic AI & Real-Time Data            ║
╚══════════════════════════════════════════════════════════════════╝

Run: python professional_enterprise_dashboard.py
"""

import os
import json
import gradio as gr
import requests
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import protos

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ═══════════════════════════════════════════════════════════════════
# TOOLS IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════

def get_live_weather(city: str, unit: str = "celsius") -> dict:
    """Get real-time weather data"""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            temp_c = float(current['temp_C'])
            temp_f = float(current['temp_F'])
            return {
                "city": city.title(),
                "temperature": temp_f if unit.lower() == "fahrenheit" else temp_c,
                "unit": unit,
                "condition": current['weatherDesc'][0]['value'],
                "humidity": f"{current['humidity']}%",
                "feels_like": float(current['FeelsLikeC']),
                "wind_speed": f"{current['windspeedKmph']} km/h",
                "pressure": current.get('pressure', 'N/A'),
                "success": True
            }
        return {"error": f"Weather data not found for '{city}'", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}

def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
    """Live currency conversion"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_curr.upper())
            if rate:
                converted = round(amount * rate, 2)
                return {
                    "original": f"{amount} {from_curr.upper()}",
                    "converted": f"{converted} {to_curr.upper()}",
                    "rate": rate,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "success": True
                }
            return {"error": f"Currency '{to_curr}' not found", "success": False}
        return {"error": "Failed to fetch exchange rates", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}

CITY_DATABASE = {
    "mumbai": {"country": "India", "timezone": "GMT+5:30", "language": "Hindi/Marathi", "currency": "INR"},
    "delhi": {"country": "India", "timezone": "GMT+5:30", "language": "Hindi", "currency": "INR"},
    "bangalore": {"country": "India", "timezone": "GMT+5:30", "language": "Kannada", "currency": "INR"},
    "hyderabad": {"country": "India", "timezone": "GMT+5:30", "language": "Telugu", "currency": "INR"},
    "london": {"country": "United Kingdom", "timezone": "GMT+1", "language": "English", "currency": "GBP"},
    "tokyo": {"country": "Japan", "timezone": "GMT+9", "language": "Japanese", "currency": "JPY"},
    "new york": {"country": "United States", "timezone": "GMT-4", "language": "English", "currency": "USD"},
    "dubai": {"country": "United Arab Emirates", "timezone": "GMT+4", "language": "Arabic", "currency": "AED"},
    "sydney": {"country": "Australia", "timezone": "GMT+10", "language": "English", "currency": "AUD"},
    "paris": {"country": "France", "timezone": "GMT+2", "language": "French", "currency": "EUR"},
    "singapore": {"country": "Singapore", "timezone": "GMT+8", "language": "English", "currency": "SGD"},
}

def get_city_info(city: str) -> dict:
    """Get city information"""
    info = CITY_DATABASE.get(city.lower().strip())
    if info:
        return {"city": city.title(), **info, "success": True}
    return {"error": f"City information not found for '{city}'", "success": False}

# ═══════════════════════════════════════════════════════════════════
# GEMINI TOOL SETUP
# ═══════════════════════════════════════════════════════════════════

TOOL_DECLARATIONS = [
    protos.Tool(function_declarations=[
        protos.FunctionDeclaration(
            name="get_live_weather",
            description="Retrieve real-time weather data for any global city",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "city": protos.Schema(type=protos.Type.STRING, description="City name"),
                    "unit": protos.Schema(type=protos.Type.STRING, description="celsius or fahrenheit"),
                },
                required=["city"],
            ),
        ),
        protos.FunctionDeclaration(
            name="convert_currency",
            description="Execute live currency conversion. Use INR for Indian Rupees.",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "amount": protos.Schema(type=protos.Type.NUMBER, description="Amount to convert"),
                    "from_curr": protos.Schema(type=protos.Type.STRING, description="Source currency"),
                    "to_curr": protos.Schema(type=protos.Type.STRING, description="Target currency"),
                },
                required=["amount", "from_curr", "to_curr"],
            ),
        ),
        protos.FunctionDeclaration(
            name="get_city_info",
            description="Retrieve comprehensive city metadata",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={"city": protos.Schema(type=protos.Type.STRING)},
                required=["city"],
            ),
        ),
    ])
]

TOOL_MAP = {
    "get_live_weather": get_live_weather,
    "convert_currency": convert_currency,
    "get_city_info": get_city_info,
}

def dispatch_tool(function_call) -> str:
    """Execute tool and return JSON"""
    name = function_call.name
    args = dict(function_call.args)
    fn = TOOL_MAP.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = fn(**args)
    return json.dumps(result, ensure_ascii=False)

# ═══════════════════════════════════════════════════════════════════
# AGENTIC LOOP
# ═══════════════════════════════════════════════════════════════════

def agent_run(user_query: str) -> tuple:
    """Execute agentic loop and return response + execution log"""
    if not GEMINI_API_KEY:
        return "ERROR: API Key not configured. Please set GEMINI_API_KEY in .env file", "Configuration Error"
    
    model = genai.GenerativeModel(
        "gemini-flash-lite-latest",
        system_instruction="""You are an enterprise-grade AI assistant specializing in:
- Real-time weather intelligence
- Currency conversion analytics (with INR support)
- Geographic and city metadata

Provide professional, data-driven responses. Always utilize available tools for real-time information."""
    )
    
    history = [{"role": "user", "parts": [user_query]}]
    execution_steps = []
    
    execution_steps.append(f"**QUERY RECEIVED:** {user_query}\n")
    execution_steps.append(f"**TIMESTAMP:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for turn in range(10):
        try:
            response = model.generate_content(history, tools=TOOL_DECLARATIONS)
            candidate = response.candidates[0]
            part = candidate.content.parts[0]
            
            if hasattr(part, "function_call") and part.function_call.name:
                fc = part.function_call
                result = dispatch_tool(fc)
                
                execution_steps.append(f"\n**TOOL INVOCATION #{turn+1}**")
                execution_steps.append(f"• Function: `{fc.name}`")
                execution_steps.append(f"• Parameters: `{dict(fc.args)}`")
                execution_steps.append(f"• Response:")
                execution_steps.append(f"```json\n{json.dumps(json.loads(result), indent=2)}\n```")
                
                history.append({"role": "model", "parts": [part]})
                history.append({
                    "role": "user",
                    "parts": [protos.Part(
                        function_response=protos.FunctionResponse(
                            name=fc.name,
                            response={"result": json.loads(result)}
                        )
                    )]
                })
            else:
                final_text = part.text.strip()
                execution_steps.append(f"\n**RESPONSE GENERATED**")
                execution_steps.append(f"**STATUS:** Success")
                log = "\n".join(execution_steps)
                return final_text, log
        
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            execution_steps.append(f"\n**ERROR ENCOUNTERED:** {str(e)}")
            log = "\n".join(execution_steps)
            return error_msg, log
    
    log = "\n".join(execution_steps)
    return "[Maximum iteration limit reached]", log

# ═══════════════════════════════════════════════════════════════════
# PROFESSIONAL ENTERPRISE CSS
# ═══════════════════════════════════════════════════════════════════

ENTERPRISE_CSS = """
/* Global Styles with Gradient Background */
body {
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    margin: 0;
    padding: 20px;
    min-height: 100vh;
}

.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    background: transparent !important;
    padding: 0 !important;
}

/* Header Section - White Card with Shadow */
.enterprise-header {
    background: rgba(255, 255, 255, 0.98);
    color: #1a202c;
    padding: 30px 40px;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
}

.enterprise-title {
    font-size: 32px;
    font-weight: 700;
    color: #1a202c;
    margin: 0;
    letter-spacing: -0.5px;
}

.enterprise-subtitle {
    font-size: 16px;
    font-weight: 500;
    color: #718096;
    margin-top: 8px;
}

/* Content Wrapper */
.content-wrapper {
    padding: 0;
}

/* Stats Cards - White Cards with Left Border */
.stat-card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    border-left: 4px solid #667eea;
}

.stat-number {
    font-size: 36px;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 8px 0;
    line-height: 1;
}

.stat-label {
    font-size: 13px;
    font-weight: 600;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Panel Design - White Cards */
.panel {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.panel-header {
    background: #f7fafc;
    padding: 16px 24px;
    border-bottom: 2px solid #e2e8f0;
    font-weight: 700;
    color: #1a202c;
    font-size: 20px;
}

.panel-body {
    padding: 24px;
}

/* Query Section */
.query-section {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    padding: 24px;
    overflow: hidden;
}

/* Response Panels */
.response-panel {
    background: white;
    padding: 20px;
    min-height: 280px;
    font-size: 15px;
    color: #2d3748;
    line-height: 1.7;
}

.execution-log {
    background: #f7fafc;
    color: #2d3748;
    padding: 20px;
    font-family: "Courier New", "Consolas", "Monaco", monospace;
    font-size: 13px;
    line-height: 1.6;
    min-height: 280px;
    overflow-y: auto;
}

/* Gradient Button */
button[type="submit"],
.primary-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 14px 28px !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 15px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

button[type="submit"]:hover,
.primary-button:hover {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    transform: translateY(-2px) !important;
}

/* Input Fields */
textarea, input[type="text"] {
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 15px !important;
    color: #2d3748 !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    background: white !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #667eea !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Tool Info Box */
.tool-info {
    background: #f7fafc;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin-top: 16px;
    font-size: 13px;
    color: #2d3748;
    line-height: 1.6;
}

.tool-info strong {
    color: #1a202c;
    font-size: 14px;
}

/* Section Title */
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 12px;
    margin-top: 20px;
}

/* Footer */
.footer {
    background: rgba(255, 255, 255, 0.98);
    padding: 24px 30px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    margin-top: 20px;
    color: #718096;
    font-size: 14px;
    font-weight: 500;
}

/* Remove Gradio defaults and gaps */
.block {
    border: none !important;
    background: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
}

.row {
    gap: 0 !important;
    margin: 0 !important;
}

.column {
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

footer {
    display: none !important;
}
"""

# ═══════════════════════════════════════════════════════════════════
# PROFESSIONAL DASHBOARD
# ═══════════════════════════════════════════════════════════════════

def create_professional_dashboard():
    """Create professional enterprise-grade dashboard"""
    
    with gr.Blocks(title="Enterprise AI Agent Platform", css=ENTERPRISE_CSS, theme=gr.themes.Soft()) as demo:
        
        # Beautiful Gradient Header
        gr.HTML("""
            <div class="enterprise-header">
                <h1 class="enterprise-title">Agentic AI Function Calling Dashboard</h1>
                <p class="enterprise-subtitle">Real-time Multi-Turn Agent Execution | Gemini Native Function Calling</p>
            </div>
        """)
        
        # Content Wrapper - Start main content
        
        # Statistics Dashboard with Modern Cards
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                    <div class="stat-card">
                        <div class="stat-number">Weather</div>
                        <div class="stat-label">Global Data</div>
                    </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                    <div class="stat-card">
                        <div class="stat-number">Currency</div>
                        <div class="stat-label">Live Rates</div>
                    </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                    <div class="stat-card">
                        <div class="stat-number">Cities</div>
                        <div class="stat-label">Geo Intelligence</div>
                    </div>
                """)
            with gr.Column(scale=1):
                gr.HTML("""
                    <div class="stat-card">
                        <div class="stat-number">AI Agent</div>
                        <div class="stat-label">Multi-Turn</div>
                    </div>
                """)
        
        # Main Interface
        with gr.Row():
            # Left Panel - Query Interface
            with gr.Column(scale=2):
                gr.HTML('<div class="query-section">')
                
                query_input = gr.Textbox(
                    label="",
                    placeholder="Ask about weather, currency, or city information...",
                    lines=4
                )
                
                submit_btn = gr.Button(
                    "Submit Query",
                    variant="primary",
                    size="lg"
                )
                
                gr.HTML('<h4 class="section-title">Quick Examples</h4>')
                gr.Examples(
                    examples=[
                        "What's the weather in Mumbai?",
                        "Convert 100 USD to INR",
                        "Tell me about Tokyo",
                        "Weather in Delhi and convert 50 EUR to INR",
                    ],
                    inputs=query_input,
                    label=""
                )
                
                gr.HTML("""
                    <div class="tool-info">
                        <strong>Integrated Services</strong><br>
                        • <strong>Weather:</strong> wttr.in (Real-time global data)<br>
                        • <strong>Currency:</strong> ExchangeRate-API (Live exchange rates + INR)<br>
                        • <strong>AI Model:</strong> Google Gemini Flash Lite (Function calling)
                    </div>
                </div>
                """)
            
            # Right Panel - Response & Logs
            with gr.Column(scale=3):
                gr.HTML('<div class="panel">')
                gr.HTML('<div class="panel-header">Agent Response</div>')
                response_output = gr.Markdown(
                    value="*Waiting for query...*",
                    elem_classes="response-panel"
                )
                gr.HTML('</div>')
                
                gr.HTML('<div class="panel" style="margin-top: 12px;">')
                gr.HTML('<div class="panel-header">Execution Log</div>')
                log_output = gr.Markdown(
                    value="*Execution details will appear here...*",
                    elem_classes="execution-log"
                )
                gr.HTML('</div>')
        
        # Event Handlers
        submit_btn.click(
            agent_run,
            inputs=[query_input],
            outputs=[response_output, log_output]
        )
        
        query_input.submit(
            agent_run,
            inputs=[query_input],
            outputs=[response_output, log_output]
        )
        
        # Modern Footer
        gr.HTML("""
            <div class="footer">
                <strong>Powered by Google Gemini API | Multi-Turn Agentic AI System</strong><br>
                <div style="margin-top: 12px;">
                    <span style="background: #edf2f7; color: #4a5568; padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: 600; margin: 0 4px;">Python</span>
                    <span style="background: #edf2f7; color: #4a5568; padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: 600; margin: 0 4px;">Gemini Flash Lite</span>
                    <span style="background: #edf2f7; color: #4a5568; padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: 600; margin: 0 4px;">Function Calling</span>
                    <span style="background: #edf2f7; color: #4a5568; padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: 600; margin: 0 4px;">Autonomous Agents</span>
                </div>
            </div>
        """)
        
        # Close Content Wrapper - End main content
    
    return demo

# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       PROFESSIONAL ENTERPRISE MULTI-AGENT AI PLATFORM           ║")
    print("║            Corporate-Grade Dashboard Solution                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    if not GEMINI_API_KEY:
        print("\n[WARNING] GEMINI_API_KEY not configured")
        print("          Configure in .env file for AI agent functionality\n")
    else:
        print("\n[SUCCESS] Gemini API authenticated")
    
    print("\n[INFO] Launching dashboard server")
    print("       URL: http://127.0.0.1:7863")
    print("       Features: Weather • Currency • City Intelligence • AI Agent\n")
    
    demo = create_professional_dashboard()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True,
        favicon_path=None
    )
