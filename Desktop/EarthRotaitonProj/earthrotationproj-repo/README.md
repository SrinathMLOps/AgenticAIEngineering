# Earth Rotation Project

A real-time interactive visualization of Earth's rotation with live solar tracking and timezone information. This project demonstrates celestial mechanics, dynamic 3D animations, and real-time data processing.

**🌍 Live Demo:** [earthrotationproj.vercel.app](https://earthrotationproj.vercel.app)

---

## ✨ Features

### 🌅 Solar Live Tracker
- **Real-time Dashboard** showing live sun position across all timezones
- **Full 4D animations** running simultaneously
- **Interactive controls** with adjustable speed
- **North Pole top-down view** with orbital mechanics
- **Spinning 3D globe** with realistic rotations
- **Live daytime terminator** for accurate day/night boundaries
- **Screenshot recorder** button for capturing moments

### 🌍 Earth Rotation Visualization
- **Dedicated animation** explaining how Earth's rotation creates day and night cycles
- **Adjustable speed controls** to slow down or speed up rotation (×1 to ×160)
- **Side view** showing the spinning globe from the equator
- **North Pole orbital view** for understanding rotational mechanics
- **Axial tilt cross-section** demonstrating Earth's 23.5° tilt
- **24-hour timeline strip** showing the complete day cycle

---

## 📊 Live Output Example

The application displays real-time celestial data with live animations:

### ☀️ Solar Live Tracker Dashboard
**Real-time UTC Time Display:**
- **18:13:49** ← UTC (Master Time)
- **18:13:49** ← Karimanagar, India (IST)
- **13:43:49** ← Coventry, UK (GMT)

**Location-Specific Information:**

🇮🇳 **Karimanagar, India**
- Current Time: 18:13:49 IST
- Sun Position: 7.2° altitude above horizon
- Status: ⚠️ **Daytime**

🇬🇧 **Coventry, UK**
- Current Time: 13:43:49 GMT
- Sun Position: 60.1° altitude above horizon
- Status: ⚠️ **Daytime**

**Seasonal Information:**
```
14 June 2026 — Summer Solstice Week
├─ Sun Declination: +23.3°N (nearly overhead Karimanagar at noon)
├─ Daylight Duration: 
│  └─ Karimanagar: 5h 30m earlier than Country daylight
│  └─ Coventry: 18h 40m daylight on Karimanagar; 13h 23m nighttime on Coventry every day
└─ Karimanagar sunrise: 5h 30m earlier than Country day
```

**Live Updates:** 🟢 Updates every second with real-time calculations

### 🌍 3D Animation Features
- Full 4D animated globe with day/night terminator
- Real-time sun position markers
- Rotating coordinate grid overlay
- North Pole top-down orbital view
- Side view with spinning globe
- Screenshot capture functionality

---

## � Live Application Interface

When you visit the live app, you'll see:

**Solar Live Tracker Dashboard:**
- 🔴 **Real-time UTC clock** at the top center
- 📍 **Dual location panels** showing time for Karimanagar, India & Coventry, UK
- ☀️ **Sun position data** with altitude angles above horizon
- 📅 **Seasonal information** including solstice/equinox data
- 🌐 **Interactive 3D globe** with animated day/night terminator
- ⚡ **Live updates** every second with precise calculations
- ⏱️ **Speed controls** to adjust animation speed (×1 to ×160)
- 📸 **Screenshot button** to capture the current visualization

---

## �🎮 How to Use

### Solar Live Tracker
1. Click **"Open Live Dashboard"** button
2. View real-time UTC time at the top
3. See location-specific times in the panels below
4. Observe the animated 3D globe with:
   - Day/night terminator line
   - Sun position markers
   - Rotating coordinate grid
5. Use speed controls to adjust animation speed
6. Click screenshot button to save current frame

### Earth Rotation Visualization
1. Click **"Open Earth Rotation"** button
2. Watch the animation cycle through:
   - Side view of spinning globe
   - North Pole orbital perspective
   - Axial tilt demonstration
   - 24-hour timeline
3. Adjust speed with the controls (×1 to ×160)
4. Explore how rotation creates day/night cycles

---

## 🛠️ Technical Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **3D Graphics:** Three.js (WebGL)
- **Animations:** Custom JavaScript animation loops
- **Real-time Data:** System time API
- **Deployment:** Vercel (serverless hosting)
- **Version Control:** Git

---

## 📁 Project Files

- `index.html` - Main entry point with navigation
- `solar-complete.html` - Solar Live Tracker dashboard
- `earth-rotation.html` - Earth Rotation visualization
- `solar-github.zip` - Archived source code

---

## 🚀 Deployment

This project is deployed on Vercel with automatic deployments from the GitHub repository.

**Live URL:** https://earthrotationproj.vercel.app

### Features:
- ✅ Production deployment
- ⚡ Automatic scaling
- 🌐 Global CDN distribution
- 📈 Real-time performance monitoring

---

## 🎓 Educational Value

This project is ideal for learning:
- **Celestial Mechanics:** How Earth's rotation creates day/night cycles
- **3D Graphics:** WebGL and Three.js rendering
- **Real-time Animation:** Smooth 60 FPS rendering
- **Timezone Calculations:** UTC offset and location-based time calculations
- **Interactive UI:** Web-based visualization design

---

## 💡 Key Concepts Demonstrated

### Earth Rotation
- **Axial tilt** of 23.5° relative to orbital plane
- **Rotation period** of 24 hours (1 sidereal day)
- **Day/night terminator** calculated in real-time

### Solar Mechanics
- **Sun declination** changes throughout the year (−23.5° to +23.5°)
- **Sunrise/Sunset times** vary by latitude and season
- **Solar altitude** changes based on location and time

### Time Zones
- **UTC (Coordinated Universal Time)** reference
- **Offset calculations** for different regions
- **Daylight offset** representation

---

## 📸 Screenshots

### Solar Live Tracker Dashboard
Shows real-time UTC time, multiple timezone displays, seasonal information, and interactive 3D globe animation.

### Earth Rotation Visualization
Dedicated view explaining Earth's rotation with multiple perspectives: side view, orbital view, and 24-hour timeline.

---

## 🔗 Links

- **Repository:** https://github.com/SrinathMLOps/earthrotationproj
- **Live Demo:** https://earthrotationproj.vercel.app
- **Author:** SrinathMLOps

---

## 📝 License

This project is open source and available for educational and personal use.

---

## 🤝 Contributing

Interested in improving this project? Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**Last Updated:** June 2026
**Status:** ✅ Live and Running on Vercel
