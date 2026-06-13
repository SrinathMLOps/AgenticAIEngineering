# Quick Reference Card

## Essential Commands

### Setup (First Time)
```bash
cd simple
python -m pip install -r requirements.txt
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run Agent (Terminal)
```bash
python main.py
```

### Run Dashboards

**Standard (Friendly):**
```bash
python dashboard.py
```

**Enterprise (Professional):**
```bash
python dashboard_enterprise.py
```

**Share (Public URL):**
```bash
python dashboard_share.py
```

### Test API Key
```bash
python test_api_key.py
```

---

## Dashboard Comparison

| Feature | Standard | Enterprise | Share |
|---------|----------|------------|-------|
| Style | Friendly | Professional | Friendly |
| Emojis | ✅ Yes | ❌ No | ✅ Yes |
| Export | ❌ No | ✅ JSON | ❌ No |
| Public URL | ❌ No | ❌ No | ✅ Yes |
| Best For | Learning | Business | Sharing |

---

## Access URLs

- **Local:** http://localhost:7860
- **Share:** https://xxx.gradio.live (generated)

---

## File Structure

```
simple/
├── main.py                    # Terminal version
├── dashboard.py               # Standard UI
├── dashboard_enterprise.py    # Professional UI
├── dashboard_share.py         # Public sharing
├── test_api_key.py           # API key tester
├── .env                       # Your API key
└── agent/loop.py             # Core logic
```

---

## Quick Fixes

**API Key Error:**
```bash
python test_api_key.py
# Then fix your .env file
```

**Port Busy:**
```python
# In dashboard file, change:
server_port=7860  # to 8080 or other port
```

**Localhost Not Working:**
```bash
# Use share version instead:
python dashboard_share.py
```

---

## When to Use Each

**Standard Dashboard:**
- Daily development
- Learning and testing
- Personal projects

**Enterprise Dashboard:**
- Client presentations
- Corporate environments
- Need audit trails
- Professional demos

**Share Dashboard:**
- Remote demonstrations
- Sharing with others
- Quick public demos

---

## Documentation Index

- [README.md](./README.md) - Overview
- [QUICK_START.md](./QUICK_START.md) - 5-minute setup
- [DASHBOARD_GUIDE.md](./DASHBOARD_GUIDE.md) - Dashboard details
- [DASHBOARD_COMPARISON.md](./DASHBOARD_COMPARISON.md) - Compare versions
- [BEGINNERS_GUIDE.md](./BEGINNERS_GUIDE.md) - Complete learning guide

---

## Support

**API Key Issues:**
1. Get key: https://console.anthropic.com/settings/keys
2. Test: `python test_api_key.py`
3. Fix `.env` file

**Dashboard Issues:**
- Check internet connection
- Verify API key
- Try different port
- Use share version as fallback

---

**Repository:** https://github.com/SrinathMLOps/AgenticAIEngineering.git
