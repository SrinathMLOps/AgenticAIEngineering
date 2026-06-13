# Screenshots Guide

## 📸 How to Add Screenshots

### Required Screenshots

To complete the README documentation, please add the following screenshots:

1. **header.png** (Optional banner image)
   - Can be a custom banner or logo for the project

2. **dashboard-interface.png** ⭐ **IMPORTANT**
   - Take a screenshot of the main dashboard interface
   - Should show: header, query input, example buttons, and execution metrics
   - Recommended size: 1920x1080 or 1280x720

3. **query-execution.png** ⭐ **IMPORTANT**
   - Screenshot showing a query being executed
   - Example: "weather in Mumbai and convert 4500 GBP to INR"
   - Should show: query input, execution logs, tool calls

4. **agent-response.png** ⭐ **IMPORTANT**
   - Screenshot showing the final agent response
   - Should display: final answer, execution logs with tool calls, metrics

## 🎯 How to Take Screenshots

### Option 1: Using Windows Snipping Tool

1. Open the dashboard at http://localhost:7860
2. Press `Windows + Shift + S` to open Snipping Tool
3. Select the area you want to capture
4. Save the screenshot with the appropriate name in this folder

### Option 2: Using Browser Screenshot

1. Open dashboard in browser
2. Press `F12` to open Developer Tools
3. Press `Ctrl + Shift + P` and type "screenshot"
4. Select "Capture full size screenshot"
5. Save with appropriate name

### Option 3: Using Third-Party Tools

- **Greenshot** (Windows)
- **ShareX** (Windows)
- **Snagit** (Windows/Mac)
- **Lightshot** (Cross-platform)

## 📝 Naming Convention

Save your screenshots with these exact names:

- `dashboard-interface.png` - Main dashboard view
- `query-execution.png` - Query with execution logs
- `agent-response.png` - Complete response with results
- `header.png` - Optional banner (optional)

## 💡 Screenshot Tips

### For Best Results:

1. **Clean Browser Window**: Hide bookmarks bar and other distractions
2. **Full Dashboard**: Capture the entire dashboard interface
3. **Readable Text**: Ensure all text is crisp and readable
4. **Good Example Query**: Use queries that demonstrate multiple tools:
   - "weather in Mumbai and convert 4500 GBP to INR"
   - "Compare weather in Delhi and Bangalore, convert 500 EUR to INR"
   - "I'm visiting Kolkata. What's the local language, weather, and convert 1000 JPY to INR?"

4. **Show Execution Logs**: Make sure tool calls and results are visible
5. **Proper Sizing**: 
   - Minimum width: 1024px
   - Maximum size: 5MB per image
   - Format: PNG (preferred) or JPG

## ✅ Recommended Screenshot Sequence

1. Start the dashboard: `python gradio_dashboard.py`
2. Wait for "Model initialized successfully"
3. Open browser at http://localhost:7860
4. **Screenshot 1**: Take full dashboard view (dashboard-interface.png)
5. Enter a query: "weather in Mumbai and convert 4500 GBP to INR"
6. Click "Execute Agent"
7. **Screenshot 2**: Capture while showing execution logs (query-execution.png)
8. Wait for complete response
9. **Screenshot 3**: Capture final result with all logs (agent-response.png)

## 🔧 After Adding Screenshots

Once you've added the screenshots:

1. Verify they display correctly in the README:
   ```bash
   # Preview README in VS Code or GitHub
   ```

2. Add and commit to git:
   ```bash
   git add screenshots/
   git add README.md
   git commit -m "Add dashboard screenshots for documentation"
   ```

3. Push to GitHub:
   ```bash
   git push origin main
   ```

## 📋 Checklist

Before pushing to GitHub:

- [ ] dashboard-interface.png added
- [ ] query-execution.png added
- [ ] agent-response.png added
- [ ] All images are clear and readable
- [ ] Images are optimized (< 5MB each)
- [ ] README.md references correct image names
- [ ] Tested images display on GitHub

---

**Need Help?**

If you're having trouble with screenshots, you can:
1. Use the static HTML dashboard (dashboard.html) for screenshots
2. Take screenshots at different stages of execution
3. Ask for help in the repository issues
