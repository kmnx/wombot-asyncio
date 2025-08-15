import aiohttp
import os
import re
import asyncio

# OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Set this in your environment
OPENWEATHER_API_KEY = "df8013e4ddd2b41ae3119ff7f287f667"


async def get_weather(location: str) -> str:
    """
    Fetch weather data for a given location (city, country, or lat/lon).
    Returns a string with weather info or an error message.
    """
    if not OPENWEATHER_API_KEY:
        return "Weather API key not set."

    # Try to parse latitude/longitude
    latlon_match = re.match(r"^\s*(-?\d+(\.\d+)?)[,\s]+(-?\d+(\.\d+)?)\s*$", location)
    if latlon_match:
        lat, lon = latlon_match.group(1), latlon_match.group(3)
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

    else:
        # Assume city/country name
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                print(f"HTTP status: {resp.status}")
                data = await resp.json()
                print(f"Response data: {data}")
                if resp.status != 200 or "weather" not in data:
                    return f"No weather data found for {location}"
                desc = data["weather"][0]["description"].capitalize()
                temp = data["main"]["temp"]
                city = data.get("name", location)
                country = data.get("sys", {}).get("country", "")
                return f"Weather for {city}, {country}: {desc}, {temp:.1f}°C"
        except Exception as e:
            print(f"Exception: {e}")
            return f"No weather data found for {location}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python weather.py <location>")
    else:
        location = " ".join(sys.argv[1:])
        weatherdata = asyncio.run(get_weather(location))
        print(weatherdata)
