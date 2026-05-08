import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from db_config import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenWeatherIntegration:
    """Integration with OpenWeather API for weather data"""
    
    def __init__(self, api_key: str):
        """
        Initialize OpenWeather API integration
        
        Args:
            api_key: OpenWeather API key (free tier or premium)
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org"
        self.db = DatabaseConnection()
        self.current_weather_endpoint = f"{self.base_url}/data/2.5/weather"
        self.historical_endpoint = f"{self.base_url}/data/3.0/onecall/timemachine"

    def _log_api_call(self, endpoint: str, status_code: int, 
                     response_time: int, records: int, error: str = None):
        """Log API call to database"""
        try:
            self.db.log_api_call('OpenWeather', endpoint, status_code, 
                               response_time, records, error)
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current weather for coordinates
        
        Args:
            latitude: District latitude
            longitude: District longitude
            
        Returns:
            Dictionary with weather data or None if failed
        """
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            start_time = time.time()
            response = requests.get(self.current_weather_endpoint, params=params, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                self._log_api_call(self.current_weather_endpoint, 200, response_time, 1)
                return self._parse_weather_data(data)
            else:
                error_msg = f"HTTP {response.status_code}"
                self._log_api_call(self.current_weather_endpoint, response.status_code, 
                                 response_time, 0, error_msg)
                logger.warning(f"OpenWeather API returned {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            self._log_api_call(self.current_weather_endpoint, 0, 0, 0, str(e))
            return None

    def get_weather_for_district(self, district_id: int, latitude: float, 
                                longitude: float, date: datetime) -> Optional[Dict]:
        """
        Get weather data for a specific district and date
        
        Args:
            district_id: District ID from database
            latitude: District latitude
            longitude: District longitude
            date: Date for which to fetch weather
            
        Returns:
            Dictionary with parsed weather data or None
        """
        # Check if data already exists
        try:
            existing = self.db.get_weather_by_district_date(district_id, date.date())
            if existing:
                logger.info(f"Weather data already exists for district {district_id} on {date.date()}")
                return existing
        except Exception as e:
            logger.warning(f"Could not check existing weather data: {e}")

        # For free tier, only get current weather
        weather_data = self.get_current_weather(latitude, longitude)
        
        if weather_data:
            weather_data['district_id'] = district_id
            weather_data['date'] = date.date()
            return weather_data
        
        return None

    def _parse_weather_data(self, api_response: Dict) -> Dict:
        """
        Parse OpenWeather API response
        
        Args:
            api_response: Raw API response
            
        Returns:
            Parsed weather data dictionary
        """
        return {
            'temperature': api_response.get('main', {}).get('temp'),
            'humidity': api_response.get('main', {}).get('humidity'),
            'rainfall': api_response.get('rain', {}).get('1h', 0),
            'wind_speed': api_response.get('wind', {}).get('speed'),
            'pressure': api_response.get('main', {}).get('pressure'),
            'cloud_coverage': api_response.get('clouds', {}).get('all'),
            'uv_index': None  # Requires separate API call in free tier
        }

    def fetch_and_store_weather(self, districts: List[Dict]) -> Tuple[int, int, int]:
        """
        Fetch weather for multiple districts and store in database
        
        Args:
            districts: List of district dictionaries with latitude and longitude
            
        Returns:
            Tuple of (successful inserts, failed inserts, total processed)
        """
        successful = 0
        failed = 0
        now = datetime.now()
        
        for district in districts:
            try:
                district_id = district.get('district_id')
                latitude = district.get('latitude')
                longitude = district.get('longitude')
                
                if not all([district_id, latitude, longitude]):
                    logger.warning(f"Incomplete district data: {district}")
                    failed += 1
                    continue
                
                weather_data = self.get_weather_for_district(
                    district_id, latitude, longitude, now
                )
                
                if weather_data:
                    # Insert into database
                    self.db.insert_weather_data(
                        district_id=weather_data['district_id'],
                        date=weather_data['date'],
                        temperature=weather_data.get('temperature'),
                        humidity=weather_data.get('humidity'),
                        rainfall=weather_data.get('rainfall'),
                        wind_speed=weather_data.get('wind_speed'),
                        pressure=weather_data.get('pressure'),
                        cloud_coverage=weather_data.get('cloud_coverage'),
                        uv_index=weather_data.get('uv_index')
                    )
                    successful += 1
                    logger.info(f"Weather data stored for district {district_id}")
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing district {district.get('district_name')}: {e}")
                failed += 1
                continue
            
            # Rate limiting (free tier: ~60 requests per minute)
            time.sleep(1)
        
        logger.info(f"Weather data fetch complete: {successful} successful, {failed} failed")
        return successful, failed, len(districts)

    def forecast_weather(self, latitude: float, longitude: float, 
                        days: int = 7) -> Optional[List[Dict]]:
        """
        Get weather forecast for next N days (requires premium API)
        
        Args:
            latitude: District latitude
            longitude: District longitude
            days: Number of days to forecast (default: 7)
            
        Returns:
            List of forecast dictionaries or None
        """
        logger.info(f"Weather forecasting requires premium OpenWeather API access")
        logger.info(f"Upgrade your API key to access forecast data")
        return None

    def calculate_anomalies(self, district_id: int, historical_mean: Dict) -> Dict:
        """
        Calculate weather anomalies compared to historical mean
        
        Args:
            district_id: District ID
            historical_mean: Dictionary with mean values for comparison
            
        Returns:
            Dictionary with anomaly values
        """
        current = self.get_current_weather(
            historical_mean.get('latitude'),
            historical_mean.get('longitude')
        )
        
        if not current:
            return {}
        
        anomalies = {
            'temperature_anom': current.get('temperature', 0) - historical_mean.get('avg_temp', 0),
            'humidity_anom': current.get('humidity', 0) - historical_mean.get('avg_humidity', 0),
            'rainfall_anom': current.get('rainfall', 0) - historical_mean.get('avg_rainfall', 0),
        }
        
        return anomalies


# Standalone functions for easy integration

def fetch_current_weather_for_all_districts(api_key: str) -> Tuple[int, int, int]:
    """Fetch current weather for all districts in database"""
    try:
        weather_api = OpenWeatherIntegration(api_key)
        db = DatabaseConnection()
        
        districts = db.get_all_districts()
        if not districts:
            logger.warning("No districts found in database")
            return 0, 0, 0
        
        return weather_api.fetch_and_store_weather(districts)
        
    except Exception as e:
        logger.error(f"Failed to fetch weather for all districts: {e}")
        return 0, 0, 0


if __name__ == "__main__":
    # Example usage
    API_KEY = "your_openweather_api_key"
    
    weather = OpenWeatherIntegration(API_KEY)
    
    # Example: Get current weather
    data = weather.get_current_weather(31.5204, 74.3587)  # Lahore coordinates
    if data:
        print("Current weather in Lahore:")
        print(f"  Temperature: {data.get('temperature')}°C")
        print(f"  Humidity: {data.get('humidity')}%")
        print(f"  Rainfall: {data.get('rainfall')}mm")
