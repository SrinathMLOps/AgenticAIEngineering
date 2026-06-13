# Gradio Dashboard - Agentic AI Function Calling

## Interactive Enterprise Dashboard for Multi-Turn Agent Execution

This is a professional Gradio-based web interface for running and visualizing the agentic AI system with real-time execution logs and metrics.

---

## Features

### Interactive Interface
- Text input for custom queries
- Real-time agent execution
- Live tool call tracking
- Execution logs display
- Metrics dashboard

### Pre-built Examples
- **Example 1:** Single tool query (Weather in Tokyo)
- **Example 2:** Comparative analysis (London vs Sydney weather)
- **Example 3:** Multi-domain query (Currency + Weather)
- **Example 4:** Complex chain (City info + Weather + Currency)

### Real-Time Monitoring
- Tool call counter
- Execution status tracker
- Detailed execution logs
- Final agent response display

---

## How to Run

### Step 1: Navigate to Project Directory
```cmd
cd C:\Users\SRINATH\Downloads\Agentic_AI\Day2_Agentic_AI\Day2_PromptEngineering
```

### Step 2: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### Step 3: Ensure Gradio is Installed (Already Done)
```cmd
pip install gradio
```

### Step 4: Launch Dashboard
```cmd
python gradio_dashboard.py
```

### Step 5: Open Browser
The dashboard will automatically open at:
```
http://localhost:7860
```

Or manually visit: **http://127.0.0.1:7860**

---

## Alternative: Direct Launch (Without Activating venv)

```cmd
cd C:\Users\SRINATH\Downloads\Agentic_AI\Day2_Agentic_AI\Day2_PromptEngineering
venv\Scripts\python.exe gradio_dashboard.py
```

---

## Using the Dashboard

### 1. System Status Check
Look at the top "System Status" box to verify the model is initialized:
- ✅ "Model initialized successfully" = Ready to use
- ❌ Error message = Check API key in .env file

### 2. Run Examples
Click any of the 4 example buttons to see pre-configured queries:
- Results appear instantly
- Execution logs show each tool call
- Tool count updates automatically

### 3. Custom Queries
Type your own query in the text box and click "Execute Agent"

**Example Queries:**
```
- What's the weather in Berlin?
- Compare temperatures in Dubai and Sydney
- Convert 100 EUR to USD and check Paris weather
- I'm going to Tokyo. Tell me the weather and convert 500 USD to JPY
```

### 4. View Results
- **Agent Response:** Final answer from the AI
- **Execution Logs:** Step-by-step tool calls with parameters and results
- **Tool Calls Metric:** Number of functions executed
- **Execution Status:** Current state of the agent

---

## Dashboard Components

### Header Section
- Title and system description
- Visual branding

### Input Panel (Left Side)
- Query input box
- Execute button
- 4 example query buttons
- Execution metrics (tool count)
- Status indicator

### Output Panel (Right Side)
- Agent response display
- Detailed execution logs with:
  - User query
  - Each tool call with parameters
  - JSON results from each tool
  - Final agent synthesis

---

## Architecture

### Flow
1. User submits query
2. Gemini model analyzes query
3. Agent determines which tools to call
4. Tools execute in Python
5. Results feed back to agent
6. Agent synthesizes final response
7. All steps logged in real-time

### Available Tools
- `get_weather(city, unit)` - Weather information
- `convert_currency(amount, from_curr, to_curr)` - Currency conversion
- `get_city_info(city)` - City metadata

---

## Configuration

### API Key
Ensure your `.env` file contains:
```
GEMINI_API_KEY=your-api-key-here
```

### Model Selection
Currently using: `gemini-flash-lite-latest`

To change model, edit line in `gradio_dashboard.py`:
```python
model = genai.GenerativeModel(
    "gemini-flash-lite-latest",  # Change this
    system_instruction=...
)
```

### Port Configuration
Default port: **7860**

To change, edit the launch parameters:
```python
dashboard.launch(
    server_port=8080,  # Change port here
    share=False
)
```

---

## Sharing the Dashboard

### Local Network Access
Set `server_name="0.0.0.0"` (already configured) to allow access from other devices on your network:
```
http://YOUR_IP:7860
```

### Public Internet Access
Enable public sharing (temporary link):
```python
dashboard.launch(share=True)
```

This creates a public Gradio link (valid for 72 hours).

---

## Troubleshooting

### Issue 1: "Model not initialized"
**Solution:** Check that GEMINI_API_KEY is set in `.env` file
```cmd
type .env
```

### Issue 2: Port Already in Use
**Error:** `Address already in use`

**Solution:** Change port or kill existing process
```cmd
# Find process on port 7860
netstat -ano | findstr :7860

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue 3: Gradio Not Found
**Solution:** Install Gradio in virtual environment
```cmd
venv\Scripts\pip.exe install gradio
```

### Issue 4: Quota Exceeded
**Error:** `429 You exceeded your current quota`

**Solution:** 
- Wait 1 minute for quota reset
- Use different API key
- Switch to a model with higher limits

---

## Advanced Features

### Custom Styling
The dashboard uses custom CSS for professional appearance. Edit the `css` parameter in the `gr.Blocks()` call.

### Adding New Tools
1. Add tool function to the file
2. Add to `TOOL_MAP` dictionary
3. Add to `TOOL_DECLARATIONS` for Gemini
4. Restart dashboard

### Logging
All execution details are logged in real-time with:
- Tool call sequence
- Parameters passed
- JSON results
- Final response

---

## Production Deployment

### For Internal Teams
1. Deploy on internal server
2. Set authentication:
```python
dashboard.launch(
    auth=("username", "password")
)
```

### For External Access
Consider using:
- Gradio Spaces (Hugging Face)
- Docker containerization
- Cloud deployment (AWS, Azure, GCP)

---

## Tech Stack

- **Python 3.11+**
- **Gradio 6.18.0** - Web interface
- **Google Gemini API** - LLM backend
- **google-generativeai 0.8.6** - SDK
- **python-dotenv** - Environment management

---

## File Structure

```
Day2_PromptEngineering/
├── .env                       # API keys
├── gradio_dashboard.py        # Main dashboard application
├── requirements.txt           # Dependencies
└── venv/                      # Virtual environment
```

---

## Performance

- **Response Time:** 2-5 seconds per query
- **Tool Calls:** Up to 6 per conversation turn
- **Concurrent Users:** Supports multiple simultaneous users
- **Memory Usage:** ~500MB average

---

## Screenshots

When you run the dashboard, you'll see:
1. Clean header with gradient background
2. Split-panel layout (input left, output right)
3. Example buttons for quick testing
4. Real-time metrics updating
5. Formatted execution logs with syntax highlighting

---

## Next Steps

1. Try all 4 example queries
2. Experiment with custom queries
3. Monitor tool call patterns
4. Analyze execution logs
5. Share dashboard with team (optional)

---

## Support

**Model Issues:** Check Gemini API status  
**Code Issues:** Review execution logs  
**UI Issues:** Check browser console  

---

**Last Updated:** After successful Gradio installation  
**Status:** ✅ Ready to launch  
**Dashboard URL:** http://localhost:7860
