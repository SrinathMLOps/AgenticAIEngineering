"""
Enterprise-Grade Gradio Dashboard for Agentic AI Function Calling
Interactive Multi-Turn Agent Execution Platform
"""

import gradio as gr
import json
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import protos

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS - LIVE DATA APIS
# ─────────────────────────────────────────────────────────────────

def get_weather(city: str, unit: str = "celsius") -> dict:
    """Return LIVE weather for any city using OpenWeatherMap API."""
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    
    # If no API key, use free wttr.in service
    if not api_key:
        try:
            # Use wttr.in - free weather service, no API key needed
            response = requests.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp_c = float(current['temp_C'])
                
                if unit.lower() == "fahrenheit":
                    temp = round(temp_c * 9/5 + 32, 1)
                    unit_display = "fahrenheit"
                else:
                    temp = temp_c
                    unit_display = "celsius"
                
                return {
                    "city": city.title(),
                    "temperature": temp,
                    "unit": unit_display,
                    "condition": current['weatherDesc'][0]['value'],
                    "humidity": f"{current['humidity']}%",
                    "wind_speed": f"{current['windspeedKmph']} km/h",
                    "feels_like": float(current['FeelsLikeC']),
                    "source": "wttr.in (live data)"
                }
        except Exception as e:
            return {"error": f"Could not fetch weather for '{city}': {str(e)}"}
    
    # OpenWeatherMap API (if key provided)
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            
            if unit.lower() == "fahrenheit":
                temp = round(temp * 9/5 + 32, 1)
                unit_display = "fahrenheit"
            else:
                unit_display = "celsius"
            
            return {
                "city": data['name'],
                "temperature": temp,
                "unit": unit_display,
                "condition": data['weather'][0]['description'].title(),
                "humidity": f"{data['main']['humidity']}%",
                "wind_speed": f"{data['wind']['speed']} m/s",
                "feels_like": data['main']['feels_like'],
                "source": "OpenWeatherMap (live data)"
            }
        else:
            return {"error": f"City '{city}' not found"}
    except Exception as e:
        return {"error": f"Weather API error: {str(e)}"}

def convert_currency(amount: float, from_curr: str, to_curr: str) -> dict:
    """Convert using LIVE exchange rates from exchangerate-api.com (free tier)."""
    try:
        # Free API - no key needed for basic usage
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data['rates']
            
            to_curr_upper = to_curr.upper()
            if to_curr_upper not in rates:
                return {"error": f"Currency '{to_curr}' not supported"}
            
            rate = rates[to_curr_upper]
            converted = round(amount * rate, 2)
            
            return {
                "original": f"{amount} {from_curr.upper()}",
                "converted": f"{converted} {to_curr.upper()}",
                "rate": rate,
                "timestamp": data['date'],
                "source": "exchangerate-api.com (live rates)"
            }
        else:
            return {"error": f"Currency '{from_curr}' not found"}
    except Exception as e:
        return {"error": f"Currency API error: {str(e)}"}

def convert_to_inr(amount: float, from_curr: str) -> dict:
    """Convert any currency to Indian Rupees (INR) using LIVE exchange rates."""
    try:
        # Special handling for INR to INR
        if from_curr.upper() == "INR":
            return {
                "original": f"{amount} INR",
                "converted": f"{amount} INR",
                "rate": 1.0,
                "message": "Already in Indian Rupees",
                "source": "direct"
            }
        
        # Try multiple APIs for better accuracy
        # API 1: exchangerate.host (more frequent updates)
        try:
            url = f"https://api.exchangerate.host/latest?base={from_curr.upper()}&symbols=INR"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'INR' in data.get('rates', {}):
                    rate = data['rates']['INR']
                    converted = round(amount * rate, 2)
                    
                    return {
                        "original": f"{amount} {from_curr.upper()}",
                        "converted": f"{converted} INR",
                        "rate": round(rate, 4),
                        "timestamp": data.get('date', 'today'),
                        "source": "exchangerate.host (live rates - frequent updates)",
                        "note": f"1 {from_curr.upper()} = {round(rate, 4)} INR"
                    }
        except:
            pass
        
        # API 2: Fallback to exchangerate-api.com
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data['rates']
            
            if 'INR' not in rates:
                return {"error": "INR rate not available"}
            
            rate = rates['INR']
            converted = round(amount * rate, 2)
            
            return {
                "original": f"{amount} {from_curr.upper()}",
                "converted": f"{converted} INR",
                "rate": round(rate, 4),
                "timestamp": data['date'],
                "source": "exchangerate-api.com (daily updates)",
                "note": f"1 {from_curr.upper()} = {round(rate, 4)} INR",
                "info": "For real-time forex rates, consider premium APIs like XE.com or OANDA"
            }
        else:
            return {"error": f"Currency '{from_curr}' not found"}
    except Exception as e:
        return {"error": f"Currency conversion error: {str(e)}"}

def get_city_info(city: str) -> dict:
    """Return LIVE city information using REST Countries API and geocoding."""
    try:
        # Use Nominatim (OpenStreetMap) for geocoding - free, no API key
        geocode_url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": city,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "AgenticAI-Dashboard/1.0"}
        
        response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200 and len(response.json()) > 0:
            location = response.json()[0]
            display_name = location.get('display_name', '')
            
            # Extract country from display name (last part)
            parts = display_name.split(', ')
            country = parts[-1] if parts else "Unknown"
            
            # Try to get more info from REST Countries API
            try:
                country_url = f"https://restcountries.com/v3.1/name/{country}"
                country_response = requests.get(country_url, timeout=10)
                
                if country_response.status_code == 200:
                    country_data = country_response.json()[0]
                    
                    # Get primary language
                    languages = country_data.get('languages', {})
                    language = list(languages.values())[0] if languages else "Unknown"
                    
                    # Get timezone
                    timezones = country_data.get('timezones', [])
                    timezone = timezones[0] if timezones else "Unknown"
                    
                    return {
                        "city": city.title(),
                        "country": country_data.get('name', {}).get('common', country),
                        "timezone": timezone,
                        "language": language,
                        "capital": country_data.get('capital', ['Unknown'])[0],
                        "currency": list(country_data.get('currencies', {}).keys())[0] if country_data.get('currencies') else "Unknown",
                        "source": "REST Countries API (live data)"
                    }
            except:
                pass
            
            # Fallback if REST Countries fails
            return {
                "city": city.title(),
                "country": country,
                "location": display_name,
                "latitude": location.get('lat'),
                "longitude": location.get('lon'),
                "source": "OpenStreetMap (live data)"
            }
        else:
            return {"error": f"City '{city}' not found"}
    except Exception as e:
        return {"error": f"City info API error: {str(e)}"}

# ─────────────────────────────────────────────────────────────────
# TOOL DECLARATIONS FOR GEMINI
# ─────────────────────────────────────────────────────────────────

TOOL_DECLARATIONS = [
    protos.Tool(function_declarations=[
        protos.FunctionDeclaration(
            name="get_weather",
            description="Get current weather for any city in the world",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "city": protos.Schema(type=protos.Type.STRING, description="City name (e.g., Mumbai, Delhi, New York, Paris)"),
                    "unit": protos.Schema(type=protos.Type.STRING, description="celsius or fahrenheit"),
                },
                required=["city"],
            ),
        ),
        protos.FunctionDeclaration(
            name="convert_to_inr",
            description="Convert any currency amount to Indian Rupees (INR) with live exchange rates",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "amount":    protos.Schema(type=protos.Type.NUMBER, description="Amount to convert"),
                    "from_curr": protos.Schema(type=protos.Type.STRING, description="Source currency code (e.g., USD, EUR, GBP, JPY)"),
                },
                required=["amount", "from_curr"],
            ),
        ),
        protos.FunctionDeclaration(
            name="convert_currency",
            description="Convert between any two currencies with live exchange rates",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "amount":    protos.Schema(type=protos.Type.NUMBER, description="Amount to convert"),
                    "from_curr": protos.Schema(type=protos.Type.STRING, description="Source currency (e.g., USD, EUR)"),
                    "to_curr":   protos.Schema(type=protos.Type.STRING, description="Target currency (e.g., INR, GBP)"),
                },
                required=["amount", "from_curr", "to_curr"],
            ),
        ),
        protos.FunctionDeclaration(
            name="get_city_info",
            description="Get country, timezone, language and other information for any city",
            parameters=protos.Schema(
                type=protos.Type.OBJECT,
                properties={
                    "city": protos.Schema(type=protos.Type.STRING, description="City name"),
                },
                required=["city"],
            ),
        ),
    ])
]

TOOL_MAP = {
    "get_weather":      get_weather,
    "convert_to_inr":   convert_to_inr,
    "convert_currency": convert_currency,
    "get_city_info":    get_city_info,
}

def dispatch(function_call) -> str:
    """Execute a Gemini FunctionCall and return JSON string result."""
    name   = function_call.name
    args   = dict(function_call.args)
    fn     = TOOL_MAP.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = fn(**args)
    return json.dumps(result, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────
# AGENT EXECUTION ENGINE
# ─────────────────────────────────────────────────────────────────

def agent_run_with_logs(user_query: str, model: genai.GenerativeModel):
    """
    Execute agentic loop and return formatted logs.
    Returns: (final_response, execution_logs, tool_count)
    """
    history = [{"role": "user", "parts": [user_query]}]
    logs = []
    tool_count = 0
    
    logs.append(f"**User Query:** {user_query}\n")
    
    for turn in range(6):
        response = model.generate_content(history, tools=TOOL_DECLARATIONS)
        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        if hasattr(part, "function_call") and part.function_call.name:
            fc = part.function_call
            result = dispatch(fc)
            tool_count += 1

            logs.append(f"**Tool Call #{tool_count}:** `{fc.name}()`")
            logs.append(f"**Parameters:** `{dict(fc.args)}`")
            logs.append(f"**Result:** ```json\n{result}\n```\n")

            history.append({"role": "model",  "parts": [part]})
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
            logs.append(f"**Agent Response:** {final_text}")
            return final_text, "\n".join(logs), tool_count

    return "[Max turns reached]", "\n".join(logs), tool_count

# ─────────────────────────────────────────────────────────────────
# GRADIO INTERFACE FUNCTIONS
# ─────────────────────────────────────────────────────────────────

def initialize_model():
    """Initialize Gemini model."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None, "ERROR: GEMINI_API_KEY not found in environment variables"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-flash-lite-latest",
        system_instruction=(
            "You are a helpful travel and finance assistant with access to:\n"
            "1. Weather information for any city worldwide\n"
            "2. Currency conversion to Indian Rupees (INR) - use convert_to_inr for INR conversions\n"
            "3. General currency conversion between any currencies\n"
            "4. City information (country, timezone, language)\n\n"
            "When converting to INR, prefer using convert_to_inr tool.\n"
            "Always call the appropriate tool before answering."
        ),
    )
    return model, "Model initialized successfully"

# Global model instance
MODEL = None
INIT_STATUS = ""

def init_on_load():
    """Initialize model on app load."""
    global MODEL, INIT_STATUS
    MODEL, INIT_STATUS = initialize_model()
    return INIT_STATUS

def process_query(user_query):
    """Process user query through agent."""
    global MODEL
    
    if not MODEL:
        return (
            "ERROR: Model not initialized. Check API key configuration.",
            "System not ready",
            0,
            "Not Ready"
        )
    
    if not user_query.strip():
        return (
            "Please enter a valid query.",
            "No query provided",
            0,
            "Waiting for input"
        )
    
    try:
        final_response, logs, tool_count = agent_run_with_logs(user_query, MODEL)
        status = f"Completed | {tool_count} tool calls executed"
        return final_response, logs, tool_count, status
    except Exception as e:
        return (
            f"Error: {str(e)}",
            f"**Error occurred:** {str(e)}",
            0,
            "Error"
        )

def run_example_1():
    return process_query("What's the weather like in Mumbai?")

def run_example_2():
    return process_query("Convert 100 USD to INR")

def run_example_3():
    return process_query("Compare weather in Delhi and Bangalore, and convert 500 EUR to INR")

def run_example_4():
    return process_query("I'm visiting Kolkata. What's the local language, current weather, and how much is 1000 JPY in INR?")

# ─────────────────────────────────────────────────────────────────
# GRADIO UI DEFINITION
# ─────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="Enterprise Agentic AI Platform",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate",
    ),
    css="""
    /* Full page light blue background */
    body {
        background: #e0f2fe !important;
        margin: 0;
        padding: 0;
    }
    
    /* Main container with light blue background */
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: #e0f2fe !important;
        padding: 0 !important;
    }
    
    .main {
        background: #e0f2fe !important;
    }
    
    /* Header styling */
    .header {
        text-align: center; 
        padding: 50px 40px;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
        color: white; 
        border-radius: 12px;
        margin: 20px 20px 40px 20px;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        position: relative;
    }
    
    .header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa, #3b82f6, #2563eb, #1d4ed8);
    }
    
    .header h1 {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header p {
        font-size: 16px;
        font-weight: 400;
        line-height: 1.6;
        color: white;
        opacity: 0.95;
    }
    
    /* Section titles */
    .section-title {
        font-size: 13px;
        font-weight: 700;
        color: #1e40af;
        margin-bottom: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-bottom: 8px;
        border-bottom: 2px solid #bfdbfe;
    }
    
    /* Card styling with white background */
    .card {
        background: white !important;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.1);
        border: 1px solid #bfdbfe;
        margin-bottom: 20px;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }
    
    /* Metrics box */
    .metric-box {
        background: white !important;
        border: 2px solid #bfdbfe;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
    
    .metric-value {
        font-size: 42px;
        font-weight: 800;
        color: #1e40af;
        line-height: 1;
        margin: 12px 0;
    }
    
    .metric-label {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 32px;
        background: white !important;
        border-top: 3px solid #bfdbfe;
        margin: 40px 20px 20px 20px !important;
        border-radius: 12px;
        font-size: 13px;
        color: #475569;
        line-height: 2;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.1);
    }
    
    .footer strong {
        color: #1e293b;
        font-weight: 600;
    }
    
    /* Tool badge */
    .tool-badge {
        display: inline-block;
        padding: 6px 12px;
        background: #dbeafe;
        color: #1e40af;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        margin: 4px;
    }
    
    /* Button enhancement */
    button {
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s !important;
        background: white !important;
        color: #1e40af !important;
        border: 2px solid #bfdbfe !important;
    }
    
    button:hover {
        background: #dbeafe !important;
        border-color: #3b82f6 !important;
    }
    
    /* Primary button styling - Execute Agent button */
    .primary {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
    }
    
    .primary:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Ensure primary button text is white */
    .primary span {
        color: white !important;
    }
    
    /* Input enhancement with white background */
    textarea, input, .input-block {
        background: white !important;
        border-radius: 8px !important;
        border: 2px solid #bfdbfe !important;
        transition: all 0.2s !important;
    }
    
    textarea:focus, input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        background: white !important;
    }
    
    /* Ensure all content blocks have white background */
    .block, .form, .wrap {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #bfdbfe !important;
    }
    
    /* Button text visibility */
    button span {
        color: inherit !important;
    }
    
    /* Column backgrounds */
    .column {
        background: transparent !important;
    }
    
    /* Row backgrounds */
    .row {
        background: transparent !important;
    }
    """
) as dashboard:
    
    # Header
    gr.HTML("""
    <div class="header">
        <h1>Enterprise Agentic AI Platform</h1>
        <p>Multi-Agent Function Calling System with Real-Time Data Integration<br>
        Powered by Google Gemini | Live Weather | Currency Exchange | Location Intelligence</p>
    </div>
    """)
    
    # Status indicator with better styling
    with gr.Row():
        status_box = gr.HTML(
            value='<div class="status-badge">System Ready - Model Initialized</div>',
        )
    
    # Main interface
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div class="section-title">Query Input</div>')
            query_input = gr.Textbox(
                label="Enter Query",
                placeholder="Example: Weather in Mumbai and convert 500 USD to INR",
                lines=3,
                show_label=False
            )
            
            submit_btn = gr.Button("Execute Agent", variant="primary", size="lg")
            
            gr.HTML('<div class="section-title" style="margin-top: 24px;">Example Queries</div>')
            with gr.Column():
                ex1_btn = gr.Button("Mumbai Weather", size="sm")
                ex2_btn = gr.Button("USD to INR Conversion", size="sm")
                ex3_btn = gr.Button("Multi-City Weather + EUR to INR", size="sm")
                ex4_btn = gr.Button("Travel Query: Kolkata (JPY to INR)", size="sm")
            
            # Metrics
            gr.HTML('<div class="section-title" style="margin-top: 24px;">Execution Metrics</div>')
            with gr.Row():
                tool_count_display = gr.Number(label="Tool Calls Executed", value=0, interactive=False)
            
            execution_status = gr.Textbox(
                label="Status",
                value="Ready",
                interactive=False
            )
    
        with gr.Column(scale=2):
            gr.HTML('<div class="section-title">Agent Response</div>')
            response_output = gr.Textbox(
                label="Final Response",
                lines=6,
                interactive=False,
                show_label=False
            )
            
            gr.HTML('<div class="section-title" style="margin-top: 20px;">Execution Logs</div>')
            logs_output = gr.Markdown(
                value="Execution logs will appear here..."
            )
    
    # Event handlers
    submit_btn.click(
        fn=process_query,
        inputs=[query_input],
        outputs=[response_output, logs_output, tool_count_display, execution_status]
    )
    
    ex1_btn.click(
        fn=run_example_1,
        outputs=[response_output, logs_output, tool_count_display, execution_status]
    )
    
    ex2_btn.click(
        fn=run_example_2,
        outputs=[response_output, logs_output, tool_count_display, execution_status]
    )
    
    ex3_btn.click(
        fn=run_example_3,
        outputs=[response_output, logs_output, tool_count_display, execution_status]
    )
    
    ex4_btn.click(
        fn=run_example_4,
        outputs=[response_output, logs_output, tool_count_display, execution_status]
    )
    
    # Footer
    gr.HTML("""
    <div class="footer">
        <div style="margin-bottom: 16px;">
            <span class="tool-badge">Live Weather API</span>
            <span class="tool-badge">Currency Exchange</span>
            <span class="tool-badge">INR Converter</span>
            <span class="tool-badge">Location Intelligence</span>
        </div>
        <div>
            <strong>Technology Stack:</strong> Python | Google Gemini API | Gradio | Function Calling | Multi-Turn Agents<br>
            <strong>Data Sources:</strong> wttr.in | exchangerate.host | OpenStreetMap | REST Countries API<br>
            <strong>Coverage:</strong> 195+ Countries | 160+ Currencies | Real-Time Updates
        </div>
    </div>
    """)

# ─────────────────────────────────────────────────────────────────
# LAUNCH
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize model before launching
    MODEL, INIT_STATUS = initialize_model()
    print(f"\n{'='*60}")
    print(f"Model Initialization: {INIT_STATUS}")
    print(f"{'='*60}\n")
    
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
