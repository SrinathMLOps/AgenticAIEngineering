"""
Enterprise Dashboard - DEMO MODE
=================================
Shows the professional UI without requiring API key
"""
import gradio as gr

def generate_demo_output():
    """Generate sample enterprise dashboard output"""
    html = """
    <div style='font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; 
                max-width: 1400px; background: #ffffff; color: #1a1a1a;'>
    
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
                    3
                </div>
                <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    Total Steps
                </div>
            </div>
            <div style='background: white; padding: 20px; border-radius: 2px; 
                        border-left: 3px solid #8b5cf6;'>
                <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                    1,247
                </div>
                <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    Input Tokens
                </div>
            </div>
            <div style='background: white; padding: 20px; border-radius: 2px; 
                        border-left: 3px solid #ec4899;'>
                <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                    856
                </div>
                <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    Output Tokens
                </div>
            </div>
            <div style='background: white; padding: 20px; border-radius: 2px; 
                        border-left: 3px solid #10b981;'>
                <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                    $0.0161
                </div>
                <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    Total Cost USD
                </div>
            </div>
            <div style='background: white; padding: 20px; border-radius: 2px; 
                        border-left: 3px solid #f59e0b;'>
                <div style='font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 5px;'>
                    2.34s
                </div>
                <div style='font-size: 13px; color: #64748b; text-transform: uppercase; 
                            letter-spacing: 0.5px;'>
                    Execution Time
                </div>
            </div>
        </div>
    </div>
    
    <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                padding: 25px; margin-bottom: 30px;'>
        <h3 style='margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #1e293b;'>
            Task Description
        </h3>
        <p style='margin: 0; font-size: 14px; line-height: 1.6; color: #475569;'>
            Compare the current weather conditions in London and New York. Provide temperature and conditions for each city.
        </p>
    </div>
    
    <div style='margin-bottom: 30px;'>
        <h2 style='margin: 0 0 20px 0; font-size: 18px; font-weight: 600; color: #1e293b;'>
            Detailed Execution Log
        </h2>
        
        <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                    margin-bottom: 20px; overflow: hidden;'>
            <div style='background: #f1f5f9; padding: 15px 25px; 
                        border-bottom: 1px solid #e2e8f0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h3 style='margin: 0; font-size: 15px; font-weight: 600; color: #1e293b;'>
                        Step 1 of 3
                    </h3>
                    <span style='font-size: 12px; color: #64748b;'>
                        523 input | 145 output tokens
                    </span>
                </div>
            </div>
            <div style='padding: 25px;'>
                <div style='background: #eff6ff; border-left: 3px solid #3b82f6; 
                            padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                    <div style='font-size: 12px; font-weight: 600; color: #1e40af; 
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                        Analysis
                    </div>
                    <div style='font-size: 14px; color: #1e3a8a; line-height: 1.6;'>
                        I need to retrieve weather data for two cities: London and New York. I will use the get_weather tool to fetch current conditions for both locations.
                    </div>
                </div>
                
                <div style='background: #fff7ed; border-left: 3px solid #f59e0b; 
                            padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                    <div style='font-size: 12px; font-weight: 600; color: #b45309; 
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                        Tool Invocation: get_weather
                    </div>
                    <pre style='background: #fefce8; padding: 12px; border-radius: 2px; 
                                margin: 0; overflow-x: auto; font-size: 13px; color: #854d0e; 
                                border: 1px solid #fef08a;'>{
  "location": "London, UK"
}</pre>
                </div>
                
                <div style='background: #f0fdf4; border-left: 3px solid #10b981; 
                            padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                    <div style='font-size: 12px; font-weight: 600; color: #047857; 
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                        Tool Result: Success
                    </div>
                    <div style='font-size: 14px; color: #065f46; line-height: 1.6;'>
                        Temperature: 12°C, Conditions: Partly Cloudy, Wind: 15 km/h, Humidity: 68%
                    </div>
                </div>
            </div>
        </div>
        
        <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                    margin-bottom: 20px; overflow: hidden;'>
            <div style='background: #f1f5f9; padding: 15px 25px; 
                        border-bottom: 1px solid #e2e8f0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h3 style='margin: 0; font-size: 15px; font-weight: 600; color: #1e293b;'>
                        Step 2 of 3
                    </h3>
                    <span style='font-size: 12px; color: #64748b;'>
                        412 input | 138 output tokens
                    </span>
                </div>
            </div>
            <div style='padding: 25px;'>
                <div style='background: #fff7ed; border-left: 3px solid #f59e0b; 
                            padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                    <div style='font-size: 12px; font-weight: 600; color: #b45309; 
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                        Tool Invocation: get_weather
                    </div>
                    <pre style='background: #fefce8; padding: 12px; border-radius: 2px; 
                                margin: 0; overflow-x: auto; font-size: 13px; color: #854d0e; 
                                border: 1px solid #fef08a;'>{
  "location": "New York, USA"
}</pre>
                </div>
                
                <div style='background: #f0fdf4; border-left: 3px solid #10b981; 
                            padding: 15px; margin-bottom: 15px; border-radius: 2px;'>
                    <div style='font-size: 12px; font-weight: 600; color: #047857; 
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;'>
                        Tool Result: Success
                    </div>
                    <div style='font-size: 14px; color: #065f46; line-height: 1.6;'>
                        Temperature: 18°C, Conditions: Clear Sky, Wind: 8 km/h, Humidity: 52%
                    </div>
                </div>
            </div>
        </div>
        
        <div style='background: white; border: 1px solid #e2e8f0; border-radius: 2px; 
                    margin-bottom: 20px; overflow: hidden;'>
            <div style='background: #f1f5f9; padding: 15px 25px; 
                        border-bottom: 1px solid #e2e8f0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h3 style='margin: 0; font-size: 15px; font-weight: 600; color: #1e293b;'>
                        Step 3 of 3
                    </h3>
                    <span style='font-size: 12px; color: #64748b;'>
                        312 input | 573 output tokens
                    </span>
                </div>
            </div>
            <div style='padding: 25px;'>
                <div style='background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                            border-radius: 2px; padding: 20px; color: white;'>
                    <div style='font-size: 14px; font-weight: 600; text-transform: uppercase; 
                                letter-spacing: 0.5px; margin-bottom: 15px;'>
                        Final Response
                    </div>
                    <div style='font-size: 15px; line-height: 1.7;'>
Based on the current weather data:

LONDON, UK:
- Temperature: 12°C
- Conditions: Partly Cloudy
- Wind Speed: 15 km/h
- Humidity: 68%

NEW YORK, USA:
- Temperature: 18°C
- Conditions: Clear Sky
- Wind Speed: 8 km/h
- Humidity: 52%

COMPARISON: New York is currently warmer than London by 6°C (18°C vs 12°C). New York also has clearer conditions and lower humidity, while London is experiencing partly cloudy weather with higher humidity and stronger winds.
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    </div>
    """
    return html


with gr.Blocks(
    title="Enterprise AI Agent Dashboard - DEMO",
    theme=gr.themes.Default(primary_hue="blue", secondary_hue="slate", neutral_hue="slate")
) as demo:
    
    gr.Markdown("""
    # Enterprise AI Agent Dashboard
    
    **DEMO MODE - Professional UI Preview**
    
    This demonstrates the enterprise-grade interface design. 
    Notice: NO EMOJIS, professional corporate styling, clean business presentation.
    """)
    
    gr.Markdown("""
    ### Key Features:
    - Professional blue corporate color scheme
    - Formal business language
    - Executive summary with KPIs
    - Detailed step-by-step analysis
    - Clean, emoji-free presentation
    """)
    
    output = gr.HTML(value=generate_demo_output())
    
    gr.Markdown("""
    ---
    
    **This is the ACTUAL output style** you'll see when running with a valid API key.
    
    To use with real data:
    1. Get valid API key from https://console.anthropic.com/settings/keys
    2. Update .env file
    3. Run: `python dashboard_enterprise.py`
    """)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Enterprise Dashboard - DEMO MODE")
    print("="*70)
    print("\nShowing professional UI preview...")
    print("No API key required for demo.\n")
    print("="*70 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        inbrowser=True
    )
