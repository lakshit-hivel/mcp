import json
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("weather")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    response = httpx.get(f"https://wttr.in/{city}?format=3")
    return response.text

@mcp.tool()
def get_aqi_info(city: str) -> str:
    """Get current AQI information for a city"""
    res = httpx.get(f"https://api.waqi.info/feed/{city}/?token=fc44204c45e2ecf1951c057592fa5687769000be")
    data = res.json()
    aqi_value = data["data"].get("aqi")
    return f"AQI {aqi_value}"


if __name__ == "__main__":
    mcp.run()