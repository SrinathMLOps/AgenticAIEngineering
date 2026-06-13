# Enterprise Agentic AI Platform - Day 2: Prompt Engineering

![Platform Banner](./screenshots/header.png)

## 🚀 Overview

A professional **Multi-Agent Function Calling System** built with Google Gemini API and Gradio, featuring real-time data integration for weather, currency conversion, and location intelligence. This project demonstrates advanced agentic AI patterns with live API integrations.

## ✨ Key Features

- **🌦️ Live Weather Data**: Real-time weather information for any city worldwide using wttr.in API
- **💱 Currency Conversion**: Live exchange rates with specialized INR (Indian Rupee) conversion support
- **🌍 Location Intelligence**: City information with country, timezone, and language data
- **🤖 Multi-Turn Agent**: Autonomous agent with function calling and tool execution
- **🎨 Professional UI**: Enterprise-grade Gradio dashboard with clean, modern design
- **📊 Execution Logs**: Detailed logging of tool calls, parameters, and results

## 🖼️ Screenshots

### Dashboard Interface
![Dashboard Interface](./screenshots/dashboard-interface.png)
*Professional blue-themed dashboard with query input and example buttons*

### Live Query Execution
![Query Execution](./screenshots/query-execution.png)
*Real-time weather and currency conversion query with execution logs*

### Agent Response
![Agent Response](./screenshots/agent-response.png)
*Detailed agent response with tool calls and formatted results*

## 🛠️ Technology Stack

- **AI Model**: Google Gemini (gemini-flash-lite-latest)
- **Framework**: Gradio 6.18.0
- **Language**: Python 3.11+
- **APIs**: 
  - wttr.in (Weather)
  - exchangerate.host (Currency)
  - OpenStreetMap Nominatim (Geocoding)
  - REST Countries API (Location data)

## 📋 Prerequisites

- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Git (for cloning the repository)

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Day2_PromptEngineering
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the template
copy .env.template .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

## 🚀 Usage

### Launch the Dashboard

```bash
python gradio_dashboard.py
```

The dashboard will be available at: **http://localhost:7860**

### Example Queries

Try these example queries to see the agent in action:

1. **Weather Query**: "What's the weather like in Mumbai?"
2. **Currency Conversion**: "Convert 100 USD to INR"
3. **Multi-Tool Query**: "Compare weather in Delhi and Bangalore, and convert 500 EUR to INR"
4. **Complex Query**: "I'm visiting Kolkata. What's the local language, current weather, and how much is 1000 JPY in INR?"

## 🏗️ Architecture

### Agent Flow

```
User Query → Gemini Model → Function Call Detection
     ↓
Tool Execution (Weather/Currency/Location)
     ↓
Result Processing → Model Response
     ↓
Final Answer to User
```

### Available Tools

1. **get_weather(city, unit)**: Fetch real-time weather data
2. **convert_to_inr(amount, from_curr)**: Convert any currency to Indian Rupees
3. **convert_currency(amount, from_curr, to_curr)**: General currency conversion
4. **get_city_info(city)**: Get city details including country, timezone, language

## 📁 Project Structure

```
Day2_PromptEngineering/
├── gradio_dashboard.py          # Main dashboard application
├── dashboard.html                # Static HTML dashboard
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
├── README.md                     # This file
├── screenshots/                  # Dashboard screenshots
├── beginner/                     # Beginner lesson files
├── intermediate/                 # Intermediate lesson files
│   ├── lesson_03_agentic_loop.py
│   ├── lesson_04_position_ablation.py
│   └── lesson_07_json_prompting.py
├── advanced/                     # Advanced lesson files
└── docs/                         # Documentation
    ├── GRADIO_DASHBOARD_README.md
    ├── LESSON_03_NOTES.md
    ├── LIVE_DATA_GUIDE.md
    ├── INR_CONVERSION_GUIDE.md
    └── EXCHANGE_RATE_ACCURACY.md
```

## 📊 Lessons Included

### Beginner
- **Lesson 01**: Build Attention Mechanism
- **Lesson 02**: Prompt Harness

### Intermediate
- **Lesson 03**: Agentic Loop with Function Calling ⭐
- **Lesson 04**: Position Ablation
- **Lesson 07**: JSON Prompting

### Advanced
- **Lesson 05**: Multi-Agent Systems
- **Lesson 06**: Attention Visualization
- **Lesson 08**: ADK Structured Prompting

## 🎯 Key Learnings

- ✅ Real-time API integration with Gemini function calling
- ✅ Multi-turn conversation handling
- ✅ Tool execution and result processing
- ✅ Professional UI/UX design with Gradio
- ✅ Error handling and graceful degradation
- ✅ Live data sources vs. mock data

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENWEATHER_API_KEY=your_openweather_key  # For premium weather features
DEFAULT_GEMINI_MODEL=gemini-flash-lite-latest
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### Model Configuration

The dashboard uses `gemini-flash-lite-latest` by default to avoid quota issues. You can change this in the code:

```python
model = genai.GenerativeModel(
    "gemini-flash-lite-latest",  # Change model here
    system_instruction="..."
)
```

## 🐛 Troubleshooting

### Model Not Initialized Error

**Problem**: Dashboard shows "ERROR: Model not initialized"

**Solution**: 
1. Check if `GEMINI_API_KEY` is set in `.env`
2. Verify the API key is valid
3. Restart the dashboard

### API Rate Limits

**Problem**: Too many requests error

**Solution**:
- Use `gemini-flash-lite-latest` instead of `gemini-1.5-flash`
- Wait a few minutes before retrying
- Check your API quota at Google AI Studio

### Currency Rate Differences

**Problem**: Exchange rates differ from Google

**Solution**: Free APIs use daily reference rates, not real-time rates. Difference of 0.05-0.1% is normal. See [EXCHANGE_RATE_ACCURACY.md](./EXCHANGE_RATE_ACCURACY.md) for details.

## 📈 Future Enhancements

- [ ] Add more tools (flight info, hotels, restaurants)
- [ ] Implement conversation history
- [ ] Add user authentication
- [ ] Deploy to cloud (Hugging Face Spaces, Railway, etc.)
- [ ] Add voice input/output
- [ ] Implement caching for API responses
- [ ] Add multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is part of the "Day 2: Agentic AI & Prompt Engineering" learning module.

## 🙏 Acknowledgments

- Google Gemini API for the LLM capabilities
- Gradio for the UI framework
- Free API providers: wttr.in, exchangerate.host, OpenStreetMap, REST Countries

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for learning Agentic AI patterns**
