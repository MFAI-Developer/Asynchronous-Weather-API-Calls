from fastapi import FastAPI, HTTPException
import httpx
from cachetools import TTLCache, cached
import os

app = FastAPI()

# OpenWeatherMap API configuration
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_API_KEY = "54ec898e7960c515153db5e84cdec94d"  # Replace this with your actual API key

# Set up an in-memory cache with a TTL of 300 seconds (5 minutes)
cache = TTLCache(maxsize=100, ttl=300)

async def fetch_weather_from_api(city: str):
    """
    Fetch weather data asynchronously from the OpenWeatherMap API.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                WEATHER_API_URL,
                params={"q": city, "appid": WEATHER_API_KEY},
                timeout=10
            )
            response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching weather data from API.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error occurred: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@cached(cache)
async def get_weather(city: str):
    """
    Retrieve weather data, using cached data if available.
    """
    return await fetch_weather_from_api(city)

@app.get("/weather/{city}")
async def weather(city: str):
    """
    API endpoint to get weather data for a given city.
    """
    try:
        weather_data = await get_weather(city)
        return weather_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
