"""
Simple — Weather Tool
=====================
Uses the free Open-Meteo API. No API key required.
"""
import requests

TOOL_DEFINITION = {
    "name": "get_weather",
    "description": (
        "Get current weather and a short forecast for any city or location. "
        "Free, no API key required. Use this when the user asks about weather, "
        "temperature, or conditions anywhere in the world."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or place (e.g. 'London', 'New York', 'Tokyo').",
            },
            "days": {
                "type": "integer",
                "description": "Number of forecast days to return (1–7, default 1).",
                "default": 1,
            },
        },
        "required": ["location"],
    },
}

# WMO weather code → human description
_WMO = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


def run(location: str, days: int = 1) -> str:
    days = min(max(int(days), 1), 7)

    # Step 1 — Geocode the location
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1},
        timeout=10,
    )
    geo.raise_for_status()
    results = geo.json().get("results")
    if not results:
        return f"Location not found: {location}"

    place = results[0]
    lat, lon = place["latitude"], place["longitude"]
    name = place.get("name", location)
    country = place.get("country", "")

    # Step 2 — Fetch weather
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=10,
    )
    weather.raise_for_status()
    data = weather.json()

    cur = data["current"]
    condition = _WMO.get(cur.get("weather_code", 0), "Unknown")

    lines = [
        f"Weather for {name}, {country}:",
        f"  Condition:   {condition}",
        f"  Temperature: {cur['temperature_2m']}°C",
        f"  Humidity:    {cur['relative_humidity_2m']}%",
        f"  Wind Speed:  {cur['wind_speed_10m']} km/h",
    ]

    if days > 1:
        lines.append("\nForecast:")
        daily = data["daily"]
        for i, date in enumerate(daily["time"]):
            cond = _WMO.get(daily["weather_code"][i], "")
            lines.append(
                f"  {date}: {daily['temperature_2m_min'][i]}–{daily['temperature_2m_max'][i]}°C, "
                f"{daily['precipitation_sum'][i]}mm rain  {cond}"
            )

    return "\n".join(lines)
