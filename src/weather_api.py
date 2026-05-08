"""
Weather API Integration Module for PakPulse AI
Fetches weather data from OpenWeatherMap API
"""

import requests
import pandas as pd
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "6928ee931cd48b308a76f92aba50ce6f")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_weather_data(city: str = "Lahore") -> pd.DataFrame:
    """
    Get weather forecast data for a city (5 days)
    
    Args:
        city: City name (e.g., "Lahore", "Karachi", "Islamabad")
        
    Returns:
        DataFrame with columns: ["date", "temperature", "humidity", "rainfall", "wind_speed", "city"]
    """
    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("cod") != "200":
            print(f"Error: {data.get('message', 'Unknown error')}")
            return pd.DataFrame(columns=["date", "temperature", "humidity", "rainfall", "wind_speed", "city"])
        
        forecasts = data.get("list", [])
        weather_data = []
        
        for forecast in forecasts:
            dt = datetime.fromtimestamp(forecast["dt"])
            main = forecast.get("main", {})
            weather = forecast.get("weather", [{}])[0]
            wind = forecast.get("wind", {})
            rain = forecast.get("rain", {})
            
            weather_data.append({
                "date": dt,
                "temperature": main.get("temp"),
                "humidity": main.get("humidity"),
                "rainfall": rain.get("3h", 0),  # Rainfall in last 3 hours
                "wind_speed": wind.get("speed", 0),
                "city": city
            })
        
        df = pd.DataFrame(weather_data)
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {str(e)}")
        return pd.DataFrame(columns=["date", "temperature", "humidity", "rainfall", "wind_speed", "city"])
    except Exception as e:
        print(f"Error processing weather data: {str(e)}")
        return pd.DataFrame(columns=["date", "temperature", "humidity", "rainfall", "wind_speed", "city"])

def get_weather_for_multiple_cities(cities: List[str] = None) -> pd.DataFrame:
    """
    Get weather data for multiple cities
    
    Args:
        cities: List of city names
        
    Returns:
        Combined DataFrame with weather data for all cities
    """
    if cities is None:
        cities = ["Lahore", "Karachi", "Islamabad", "Faisalabad"]
    
    all_data = []
    for city in cities:
        df = get_weather_data(city)
        if not df.empty:
            all_data.append(df)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["date", "temperature", "humidity", "rainfall", "wind_speed", "city"])
