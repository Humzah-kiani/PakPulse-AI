"""
Data Loading Module for PakPulse AI
Handles loading and extraction of disease risk data and district metadata
Supports both file-based and API-based data loading
"""

import pandas as pd
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings

# Base data directory
DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "api_cache"

class DataLoader:
    """Class to handle data loading operations"""
    
    def __init__(self, data_dir: Optional[Path] = None, use_api: Optional[bool] = None, use_who: bool = False):
        """
        Initialize DataLoader
        
        Args:
            data_dir: Path to data directory. Defaults to project data/ folder
            use_api: Whether to use API (None = auto-detect from config)
            use_who: Whether to use WHO GHO API for disease data
        """
        self.data_dir = data_dir or DATA_DIR
        self._disease_data = None
        self._districts_metadata = None
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_who = use_who
        
        # Initialize API config
        try:
            from src.api_config import APIConfig
            self.api_config = APIConfig()
            # Auto-detect API usage if not specified
            if use_api is None:
                self.use_api = self.api_config.is_enabled()
            else:
                self.use_api = use_api
        except ImportError:
            self.api_config = None
            self.use_api = False
    
    def load_disease_data(self, file_format: str = "csv", 
                         district: Optional[str] = None,
                         disease: Optional[str] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load disease risk data from WHO API, custom API, or CSV/JSON file
        
        Args:
            file_format: "csv" or "json" (only used if API is disabled)
            district: Optional district filter
            disease: Optional disease filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            DataFrame with disease risk data
        """
        # Try WHO API first if enabled
        if self.use_who:
            try:
                df = self._load_disease_data_from_who()
                if df is not None and not df.empty:
                    # Apply filters
                    if district:
                        df = df[df['district'] == district]
                    if disease:
                        df = df[df['disease'] == disease]
                    if start_date:
                        start = pd.to_datetime(start_date)
                        df = df[df['date'] >= start]
                    if end_date:
                        end = pd.to_datetime(end_date)
                        df = df[df['date'] <= end]
                    
                    self._disease_data = df
                    return df
            except Exception as e:
                print(f"Warning: WHO API load failed, trying other sources: {str(e)}")
        
        # Try custom API if enabled
        if self.use_api and self.api_config:
            try:
                df = self._load_disease_data_from_api(
                    district=district,
                    disease=disease,
                    start_date=start_date,
                    end_date=end_date
                )
                if df is not None and not df.empty:
                    self._disease_data = df
                    return df
            except Exception as e:
                print(f"Warning: API load failed, falling back to file: {str(e)}")
        
        # Fallback to file-based loading
        if file_format.lower() == "csv":
            file_path = self.data_dir / "disease_risk_data.csv"
        else:
            file_path = self.data_dir / "disease_risk_data.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        if file_format.lower() == "csv":
            df = pd.read_csv(file_path)
        else:
            with open(file_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        
        # Apply filters if provided
        if district:
            df = df[df['district'] == district]
        if disease:
            df = df[df['disease'] == disease]
        if start_date:
            start = pd.to_datetime(start_date)
            df = df[df['date'] >= start]
        if end_date:
            end = pd.to_datetime(end_date)
            df = df[df['date'] <= end]
        
        # Convert date column to datetime if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        self._disease_data = df
        return df
    
    def load_districts_geojson(self) -> Dict:
        """
        Load districts GeoJSON file
        
        Returns:
            Dictionary with GeoJSON structure
        """
        geojson_path = self.data_dir / "districts.geojson"
        
        if not geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON file not found: {geojson_path}")
        
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        return geojson
    
    def load_districts_metadata(self, file_format: str = "csv",
                               district: Optional[str] = None,
                               province: Optional[str] = None) -> pd.DataFrame:
        """
        Load districts metadata (coordinates, provinces, etc.) from API or file
        
        Args:
            file_format: "csv" or "json" (only used if API is disabled)
            district: Optional district filter
            province: Optional province filter
            
        Returns:
            DataFrame with districts metadata
        """
        # Try API first if enabled
        if self.use_api and self.api_config:
            try:
                df = self._load_districts_metadata_from_api(
                    district=district,
                    province=province
                )
                if df is not None and not df.empty:
                    self._districts_metadata = df
                    return df
            except Exception as e:
                print(f"Warning: API load failed, falling back to file: {str(e)}")
        
        # Fallback to file-based loading
        if file_format.lower() == "csv":
            file_path = self.data_dir / "districts_metadata.csv"
        else:
            file_path = self.data_dir / "districts_metadata.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")
        
        if file_format.lower() == "csv":
            df = pd.read_csv(file_path)
        else:
            with open(file_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        
        # Apply filters if provided
        if district:
            df = df[df['district'] == district]
        if province:
            df = df[df['province'] == province]
        
        self._districts_metadata = df
        return df
    
    def get_disease_data_by_district(self, district: str) -> pd.DataFrame:
        """
        Get disease data for a specific district
        
        Args:
            district: District name
            
        Returns:
            DataFrame filtered by district
        """
        if self._disease_data is None:
            self.load_disease_data()
        
        return self._disease_data[self._disease_data['district'] == district].copy()
    
    def get_disease_data_by_disease(self, disease: str) -> pd.DataFrame:
        """
        Get disease data for a specific disease type
        
        Args:
            disease: Disease name (dengue, malaria, cholera, etc.)
            
        Returns:
            DataFrame filtered by disease
        """
        if self._disease_data is None:
            self.load_disease_data()
        
        return self._disease_data[self._disease_data['disease'] == disease].copy()
    
    def get_disease_data_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get disease data within a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame filtered by date range
        """
        if self._disease_data is None:
            self.load_disease_data()
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        mask = (self._disease_data['date'] >= start) & (self._disease_data['date'] <= end)
        return self._disease_data[mask].copy()
    
    def get_latest_risk_data(self, district: Optional[str] = None, 
                            disease: Optional[str] = None,
                            include_weather: bool = False) -> pd.DataFrame:
        """
        Get the latest risk data (most recent date)
        Optionally includes weather data
        
        Args:
            district: Optional district filter
            disease: Optional disease filter
            include_weather: Whether to fetch and include weather data
            
        Returns:
            DataFrame with latest risk data (and weather if requested)
        """
        if self._disease_data is None:
            self.load_disease_data()
        
        df = self._disease_data.copy()
        
        # Apply filters
        if district:
            df = df[df['district'] == district]
        if disease:
            df = df[df['disease'] == disease]
        
        # Get latest date
        latest_date = df['date'].max()
        result_df = df[df['date'] == latest_date].copy()
        
        # Add weather data if requested
        if include_weather:
            try:
                from src.weather_api import WeatherAPI
                weather_api = WeatherAPI()
                
                weather_data_list = []
                for _, row in result_df.iterrows():
                    lat = row.get('latitude', row.get('lat'))
                    lon = row.get('longitude', row.get('lon'))
                    dist = row.get('district')
                    
                    if lat and lon:
                        weather = weather_api.get_current_weather(lat, lon, dist)
                        weather_data_list.append(weather)
                    else:
                        weather_data_list.append({})
                
                # Add weather columns to dataframe
                if weather_data_list:
                    weather_df = pd.DataFrame(weather_data_list)
                    result_df = pd.concat([result_df.reset_index(drop=True), 
                                         weather_df.reset_index(drop=True)], axis=1)
            except Exception as e:
                print(f"Warning: Could not fetch weather data: {str(e)}")
        
        return result_df
    
    def get_district_coordinates(self, district: str) -> Tuple[float, float]:
        """
        Get coordinates for a specific district
        
        Args:
            district: District name
            
        Returns:
            Tuple of (latitude, longitude)
        """
        if self._districts_metadata is None:
            self.load_districts_metadata()
        
        district_data = self._districts_metadata[
            self._districts_metadata['district'] == district
        ]
        
        if district_data.empty:
            raise ValueError(f"District '{district}' not found in metadata")
        
        lat = district_data.iloc[0]['latitude']
        lon = district_data.iloc[0]['longitude']
        return (lat, lon)
    
    def get_all_districts(self) -> List[str]:
        """
        Get list of all districts
        
        Returns:
            List of district names
        """
        if self._districts_metadata is None:
            self.load_districts_metadata()
        
        return self._districts_metadata['district'].tolist()
    
    def get_all_diseases(self) -> List[str]:
        """
        Get list of all diseases configured in the system
        Includes all diseases with API integrations, even if no data is currently available
        
        Returns:
            List of disease names
        """
        # All diseases configured with API integrations
        # Includes working APIs + other configured APIs
        all_configured_diseases = [
            "Covid-19",      # Disease.sh API
            "Dengue",       # Epidemic Forecasting API
            "Influenza",    # WHO GHO API
            "Malaria",      # WHO GHO API
            "Cholera",      # WHO GHO API
            "Pneumonia",    # Local CSV
            "Tuberculosis", # Local CSV
            "Typhoid",      # Local CSV
            "Hepatitis-A",  # Local CSV
            "Hepatitis-E",
            "Measles",
            "Mumps",
            "Whooping-Cough",
            "Polio",
            "Rotavirus",
            "Diarrhea",
            "Food-Poisoning",
            "Skin-Infection",
            "Eye-Infection",
            "Heatstroke"
        ]
        
        # Also check what diseases are in the actual data
        if self._disease_data is None:
            try:
                self.load_disease_data()
            except:
                pass
        
        # Combine configured diseases with any diseases found in data
        diseases_from_data = []
        if self._disease_data is not None and not self._disease_data.empty:
            diseases_from_data = self._disease_data['disease'].unique().tolist()
        
        # Merge and return unique sorted list
        all_diseases = list(set(all_configured_diseases + diseases_from_data))
        return sorted(all_diseases)
    
    def get_district_risk_summary(self, district: str) -> Dict:
        """
        Get risk summary for a district (all diseases, latest data)
        
        Args:
            district: District name
            
        Returns:
            Dictionary with risk summary
        """
        latest_data = self.get_latest_risk_data(district=district)
        
        summary = {
            'district': district,
            'date': latest_data['date'].max().strftime('%Y-%m-%d') if not latest_data.empty else None,
            'diseases': {}
        }
        
        for _, row in latest_data.iterrows():
            summary['diseases'][row['disease']] = {
                'risk_index': int(row['risk_index']),
                'cases_reported': int(row['cases_reported']) if 'cases_reported' in row else None
            }
        
        return summary
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """
        Generate cache key from endpoint and parameters
        
        Args:
            endpoint: API endpoint name
            params: Request parameters
            
        Returns:
            Cache key string
        """
        import hashlib
        key_str = f"{endpoint}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """
        Get cached API response
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        try:
            # Check if cache is still valid
            cache_age = time.time() - cache_file.stat().st_mtime
            cache_duration = self.api_config.get_cache_duration() if self.api_config else 300
            
            if cache_age > cache_duration:
                # Cache expired
                cache_file.unlink()
                return None
            
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_cached_data(self, cache_key: str, data: Dict) -> None:
        """
        Save API response to cache
        
        Args:
            cache_key: Cache key
            data: Data to cache
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {str(e)}")
    
    def _make_api_request(self, endpoint_name: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with retry logic and error handling
        
        Args:
            endpoint_name: Name of endpoint (disease_risk_data, districts)
            params: Query parameters
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        if not self.api_config:
            raise ValueError("API config not initialized")
        
        url = self.api_config.get_endpoint(endpoint_name)
        headers = {
            "Content-Type": "application/json",
            **self.api_config.get_auth_headers()
        }
        params = params or {}
        timeout = self.api_config.get_timeout()
        retry_attempts = self.api_config.get_retry_attempts()
        
        # Check cache first
        cache_key = self._get_cache_key(endpoint_name, params)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Make request with retries
        last_error = None
        for attempt in range(retry_attempts):
            try:
                auth_creds = self.api_config.get_auth_credentials()
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    auth=auth_creds
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Cache successful response
                self._save_cached_data(cache_key, data)
                
                return data
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _load_disease_data_from_api(self, district: Optional[str] = None,
                                   disease: Optional[str] = None,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load disease risk data from API
        
        Args:
            district: Optional district filter
            disease: Optional disease filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with disease data or None if API fails
        """
        params = {}
        if district:
            params["district"] = district
        if disease:
            params["disease"] = disease
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        try:
            response_data = self._make_api_request("disease_risk_data", params)
            
            # Handle different response formats
            if isinstance(response_data, dict):
                if response_data.get("status") == "success":
                    data_list = response_data.get("data", [])
                elif "data" in response_data:
                    data_list = response_data["data"]
                else:
                    data_list = [response_data]
            elif isinstance(response_data, list):
                data_list = response_data
            else:
                raise ValueError(f"Unexpected API response format: {type(response_data)}")
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list)
            
            # Convert date column to datetime if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
        except Exception as e:
            print(f"Error loading disease data from API: {str(e)}")
            return None
    
    def _load_disease_data_from_who(self) -> Optional[pd.DataFrame]:
        """
        Load disease data from WHO GHO API
        
        Returns:
            DataFrame with disease data in PakPulse format or None if fails
        """
        try:
            from src.who_api import get_who_data_for_multiple_diseases, transform_who_data_to_risk_format
            
            # Fetch WHO data
            who_df = get_who_data_for_multiple_diseases(
                diseases=["malaria", "cholera", "influenza"],
                country="PAK"
            )
            
            if who_df.empty:
                print("Warning: WHO API returned no data")
                return None
            
            # Load districts metadata for transformation
            if self._districts_metadata is None:
                try:
                    self.load_districts_metadata(use_api=False)
                except:
                    pass
            
            # Transform WHO data to PakPulse format
            risk_df = transform_who_data_to_risk_format(who_df, self._districts_metadata)
            
            return risk_df
        except ImportError:
            print("Warning: WHO API module not available")
            return None
        except Exception as e:
            print(f"Error loading WHO data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_districts_metadata_from_api(self, district: Optional[str] = None,
                                          province: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load districts metadata from API
        
        Args:
            district: Optional district filter
            province: Optional province filter
            
        Returns:
            DataFrame with districts metadata or None if API fails
        """
        params = {}
        if district:
            params["district"] = district
        if province:
            params["province"] = province
        
        try:
            response_data = self._make_api_request("districts", params)
            
            # Handle different response formats
            if isinstance(response_data, dict):
                if response_data.get("status") == "success":
                    data_list = response_data.get("data", [])
                elif "data" in response_data:
                    data_list = response_data["data"]
                else:
                    data_list = [response_data]
            elif isinstance(response_data, list):
                data_list = response_data
            else:
                raise ValueError(f"Unexpected API response format: {type(response_data)}")
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list)
            return df
        except Exception as e:
            print(f"Error loading districts metadata from API: {str(e)}")
            return None


# Convenience functions for direct use
def load_disease_data(file_format: str = "csv") -> pd.DataFrame:
    """Convenience function to load disease data"""
    loader = DataLoader()
    return loader.load_disease_data(file_format)


def load_districts_metadata(file_format: str = "csv") -> pd.DataFrame:
    """Convenience function to load districts metadata"""
    loader = DataLoader()
    return loader.load_districts_metadata(file_format)


def get_district_coordinates(district: str) -> Tuple[float, float]:
    """Convenience function to get district coordinates"""
    loader = DataLoader()
    return loader.get_district_coordinates(district)

try:
    import streamlit as st
    @st.cache_data(ttl=3600)
    def _cached_csv_read(path, dtype_dict):
        # Only read necessary columns to speed up loading
        cols_to_read = list(dtype_dict.keys())
        return pd.read_csv(path, low_memory=False, dtype=dtype_dict, usecols=cols_to_read)
except ImportError:
    def _cached_csv_read(path, dtype_dict):
        return pd.read_csv(path, low_memory=False, dtype=dtype_dict)

def load_pakpulse_csv_dataset(csv_path: str = None, start_year: int = None) -> pd.DataFrame:
    """
    Load the pakpulse_250k_realistic.csv dataset and convert it to standard format
    
    NOTE: This function now uses optimized vectorized operations
    for better performance with large datasets (250k+ records)
    
    Args:
        csv_path: Path to the CSV file. If None, looks for it in Desktop or data directory
        start_year: Optional start year filter applied BEFORE expensive heavy processing
    
    Returns:
        DataFrame in standard PakPulse format with columns:
        [district, latitude, longitude, disease, risk_index, date, cases_reported, population]
    """
    import os
    from pathlib import Path
    
    # Try to find the CSV file
    if csv_path is None:
        candidates = [
            Path("pakpulse_250k_realistic.csv"),  # Current directory
            Path.cwd() / "pakpulse_250k_realistic.csv",  # CWD
            Path.home() / "Desktop" / "pakpulse_250k_realistic.csv",  # Desktop
            DATA_DIR / "pakpulse_250k_realistic.csv",  # data directory
        ]
        
        # For Streamlit: also check parent directory
        try:
            import streamlit as st
            streamlit_dir = Path(__file__).parent.parent
            candidates.append(streamlit_dir / "pakpulse_250k_realistic.csv")
        except:
            pass
        
        csv_path = None
        for candidate in candidates:
            if candidate.exists():
                csv_path = str(candidate)
                print(f"Found CSV at: {csv_path}")
                break
        
        if csv_path is None:
            raise FileNotFoundError(
                f"pakpulse_250k_realistic.csv not found in any of: {[str(c) for c in candidates]}"
            )
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file found at {csv_path} but it is missing.")
    
    # NEW PERSISTENT PARQUET CACHE OPTIMIZATION
    parquet_path = Path(csv_path).with_suffix('.parquet')
    if start_year is not None:
        # Use a year-specific parquet for even faster loading if we have many records
        parquet_path = Path(csv_path).parent / f"pakpulse_data_{start_year}.parquet"
    
    if parquet_path.exists():
        print(f"Loading pre-processed dataset from CACHE: {parquet_path}")
        try:
            # Parquet loading is 50x faster than CSV + processing
            df_parquet = pd.read_parquet(parquet_path)
            print(f"Instant load complete: {len(df_parquet):,} records")
            return df_parquet
        except Exception as e:
            print(f"Parquet cache read failed, falling back to CSV: {e}")

    print(f"Loading and processing dataset from: {csv_path}")
    
    # Load CSV with optimized dtypes
    dtypes = {
        'date': 'object',
        'district': 'object',
        'lat': 'float32',
        'lon': 'float32',
        'disease': 'object',
        'cases': 'float32',
        'temperature': 'float32', 
        'humidity': 'float32',
        'rainfall': 'float32',
        'population_density': 'float32',
        'sanitation_index': 'float32',
    }
    
    try:
        df = _cached_csv_read(csv_path, dtypes)
    except Exception:
        # Fallback without specified dtypes
        df = pd.read_csv(csv_path, low_memory=False)
    
    print(f"Loaded {len(df):,} records from CSV")
    
    # Normalize disease names - keep original case for better filtering
    # The dashboard works better with title-cased disease names
    disease_mapping = {
        "COVID-19": "COVID-19",
        "covid-19": "COVID-19",
        "Covid-19": "COVID-19",
        "Dengue": "Dengue",
        "dengue": "Dengue",
        "Malaria": "Malaria",
        "malaria": "Malaria",
        "Cholera": "Cholera",
        "cholera": "Cholera",
        "Influenza": "Influenza",
        "influenza": "Influenza",
        "Flu": "Influenza",
        "flu": "Influenza",
    }
    
    if 'disease' in df.columns:
        df['disease'] = df['disease'].str.strip()
        # Map known diseases, keep others as-is (they're already properly formatted)
        df['disease'] = df['disease'].map(disease_mapping).fillna(df['disease'])
    
    # Map columns to standard format - MUST happen before risk calculation
    column_mapping = {
        'lat': 'latitude',
        'lon': 'longitude',
        'cases': 'cases_reported'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    # Also keep 'cases' column for backwards compatibility with prediction_explain
    if 'cases_reported' in df.columns and 'cases' not in df.columns:
        df['cases'] = df['cases_reported']
    
    # Ensure date column is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # CRITICAL PERFORMANCE OPTIMIZATION: Filter rows BEFORE heavy processing
    if start_year is not None and 'date' in df.columns:
        df = df[df['date'].dt.year >= start_year].copy()
        print(f"Filtered to {len(df):,} records for years >= {start_year}")
        if df.empty:
            return df
    
    # ===== VECTORIZED RISK CALCULATION (MUCH FASTER THAN ITERROWS) =====
    print("Calculating risk indices using vectorized operations...")
    
    # Calculate cases per 100k first (vectorized)
    population_density = df['population_density'].fillna(1000).values
    estimated_population = population_density * 5000
    # Use cases_reported if available, else cases, else zeros
    if 'cases_reported' in df.columns:
        cases = df['cases_reported'].fillna(0).values
    elif 'cases' in df.columns:
        cases = df['cases'].fillna(0).values
    else:
        cases = np.zeros(len(df))
    cases_per_100k = (cases / (estimated_population + 1)) * 100000
    
    # Import numpy for vectorized operations
    import numpy as np
    
    # Vectorized calculation of risk index based on disease type
    diseases_lower = df['disease'].str.lower().values
    risk_indices = np.zeros(len(df))
    
    # Empirical disease risk thresholds based on WHO epidemiological data
    # These are calibrated for actual observed case distributions
    thresholds_map = {
        "dengue": (5, 20, 50, 150),           # Mosquito-borne, fast spread
        "malaria": (10, 40, 100, 300),        # Mosquito-borne, persistent
        "cholera": (0.5, 5, 20, 100),         # Waterborne, outbreak-based
        "covid-19": (1, 10, 50, 200),         # Highly contagious respiratory
        "covid19": (1, 10, 50, 200),
        "influenza": (5, 50, 200, 1000),      # Seasonal respiratory
        "diarrhea": (5, 20, 50, 150),         # Waterborne/foodborne
        "hepatitis a": (0.1, 1, 5, 20),       # Waterborne/foodborne
        "hepatitis e": (0.1, 1, 5, 20),
        "eye infection": (5, 20, 50, 150),    # Environmental/contact
        "food poisoning": (5, 20, 50, 150),   # Foodborne
        "heatstroke": (10, 50, 100, 200),     # Environmental
        "measles": (0.5, 5, 20, 100),         # Highly contagious
        "mumps": (0.5, 5, 20, 100),
        "pneumonia": (5, 20, 50, 150),        # Respiratory
        "polio": (0.01, 0.1, 1, 10),          # Rare, vaccine-preventable
        "rotavirus": (5, 20, 50, 150),        # Enteric
        "skin infection": (5, 20, 50, 150),   # Contact/environmental
        "tuberculosis": (1, 10, 50, 200),     # Respiratory, chronic
        "typhoid": (0.5, 5, 20, 100),         # Waterborne/foodborne
        "whooping cough": (1, 10, 50, 200),   # Respiratory
    }
    
    # Calculate risk for each disease
    for disease_key, (low, moderate, high, very_high) in thresholds_map.items():
        mask = diseases_lower == disease_key
        if mask.sum() == 0:
            continue
        
        cases_vals = cases_per_100k[mask]
        
        # Vectorized piecewise calculation - scaled to full 0-100 range
        risk = np.zeros_like(cases_vals)
        
        # Low risk: 0-20
        low_mask = cases_vals < low
        risk[low_mask] = (cases_vals[low_mask] / low) * 20
        
        # Moderate risk: 20-40
        moderate_mask = (cases_vals >= low) & (cases_vals < moderate)
        risk[moderate_mask] = 20 + ((cases_vals[moderate_mask] - low) / (moderate - low)) * 20
        
        # High risk: 40-60
        high_mask = (cases_vals >= moderate) & (cases_vals < high)
        risk[high_mask] = 40 + ((cases_vals[high_mask] - moderate) / (high - moderate)) * 20
        
        # Very high risk: 60-80
        very_high_mask = (cases_vals >= high) & (cases_vals < very_high)
        risk[very_high_mask] = 60 + ((cases_vals[very_high_mask] - high) / (very_high - high)) * 20
        
        # Critical risk: 80-100
        critical_mask = cases_vals >= very_high
        risk[critical_mask] = 80 + ((cases_vals[critical_mask] - very_high) / (very_high * 2)) * 20
        risk[critical_mask] = np.minimum(100, risk[critical_mask])
        
        risk_indices[mask] = risk
    
    # For unmapped diseases, use dengue thresholds as default
    unmapped = np.array([d not in thresholds_map for d in diseases_lower])
    if unmapped.sum() > 0:
        cases_vals = cases_per_100k[unmapped]
        low, moderate, high, very_high = thresholds_map["dengue"]
        
        risk = np.zeros_like(cases_vals)
        low_mask = cases_vals < low
        risk[low_mask] = (cases_vals[low_mask] / low) * 20
        moderate_mask = (cases_vals >= low) & (cases_vals < moderate)
        risk[moderate_mask] = 20 + ((cases_vals[moderate_mask] - low) / (moderate - low)) * 20
        high_mask = (cases_vals >= moderate) & (cases_vals < high)
        risk[high_mask] = 40 + ((cases_vals[high_mask] - moderate) / (high - moderate)) * 20
        very_high_mask = (cases_vals >= high) & (cases_vals < very_high)
        risk[very_high_mask] = 60 + ((cases_vals[very_high_mask] - high) / (very_high - high)) * 20
        critical_mask = cases_vals >= very_high
        risk[critical_mask] = 80 + ((cases_vals[critical_mask] - very_high) / (very_high * 2)) * 20
        risk[critical_mask] = np.minimum(100, risk[critical_mask])
        
        risk_indices[unmapped] = risk
    
    df['risk_index'] = risk_indices
    
    # Apply environmental adjustments (vectorized)
    print("Applying environmental adjustments...")
    temp = df['temperature'].fillna(25).values
    humidity = df['humidity'].fillna(50).values
    rainfall = df['rainfall'].fillna(0).values
    sanitation = df['sanitation_index'].fillna(50).values
    
    env_factor = np.ones(len(df))
    
    # Mosquito-borne disease adjustments
    mosquito_diseases = np.array([d.lower() in ['dengue', 'malaria'] for d in df['disease']])
    env_factor[mosquito_diseases & (temp > 25) & (humidity > 60)] += 0.1
    env_factor[mosquito_diseases & (rainfall > 50)] += 0.05
    
    # Poor sanitation adjustment
    env_factor[sanitation < 50] += 0.1
    
    # Apply environmental factor
    df['risk_index'] = (df['risk_index'] * env_factor).clip(0, 100)
    
    # Calculate population
    df['population'] = (population_density * 5000).astype(int)
    
    # Select and rename columns to standard format
    standard_columns = {
        'district': 'district',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'disease': 'disease',
        'risk_index': 'risk_index',
        'date': 'date',
        'cases_reported': 'cases_reported'
    }
    
    # Build result DataFrame with proper column order
    result_data = {}
    for std_col, csv_col in standard_columns.items():
        if csv_col in df.columns:
            result_data[std_col] = df[csv_col]
    
    # Add population
    result_data['population'] = df['population']
    
    # â”€â”€ Preserve extra columns needed by prediction_explain (model features) â”€â”€
    # These are in the raw CSV and used directly by the LightGBM model
    extra_cols = [
        'cases',         # original case count (model feature)
        'lag_1', 'lag_2', 'lag_3',
        'cases_roll_mean_3', 'cases_roll_mean_7', 'cases_roll_mean_14',
        'cases_roll_std_3', 'cases_roll_std_7', 'cases_roll_std_14',
        'temperature', 'humidity', 'rainfall',
        'population_density', 'sanitation_index',
    ]
    for col in extra_cols:
        if col in df.columns and col not in result_data:
            result_data[col] = df[col]
    
    result_df = pd.DataFrame(result_data)
    
    # Save to persistent parquet cache for next time
    if not result_df.empty:
        try:
            print(f"Saving processed data to persistent cache: {parquet_path}")
            result_df.to_parquet(parquet_path, compression='snappy')
        except Exception as e:
            print(f"Could not save parquet cache: {e}")
            
    return result_df

@st.cache_resource(ttl=3600)
def _get_memory_cached_data(start_year, end_year, use_csv):
    """
    Ultra-fast memory-resident cache for the entire dataset.
    Bypasses serialization to achieve sub-second loading.
    """
    return _load_combined_api_data_internal(start_year, end_year, use_csv)

def load_combined_api_data(start_year: int = 2015, end_year: int = 2027, use_csv_dataset: bool = True) -> pd.DataFrame:
    """
    Load comprehensive disease data with sub-second performance.
    """
    try:
        import streamlit as st
        return _get_memory_cached_data(start_year, end_year, use_csv_dataset)
    except Exception:
        return _load_combined_api_data_internal(start_year, end_year, use_csv_dataset)

def _load_combined_api_data_internal(start_year: int = 2015, end_year: int = 2027, use_csv_dataset: bool = True) -> pd.DataFrame:
    """
    Internal logic for loading data from CSV and APIs.
    """
    all_data = []
    api_start = start_year  # Default initialization
    
    # 1. Load CSV dataset (if enabled and available)
    if use_csv_dataset:
        try:
            print("=" * 60)
            print("Loading pakpulse_250k_realistic.csv Dataset")
            print("=" * 60)
            print()
            
            csv_df = load_pakpulse_csv_dataset(start_year=start_year)
            
            if not csv_df.empty:
                # Filter by exact date range if needed (already mostly filtered by start_year)
                if 'date' in csv_df.columns:
                    csv_df = csv_df[
                        (csv_df['date'].dt.year >= start_year) & 
                        (csv_df['date'].dt.year <= end_year)
                    ]
                
                print(f"\n* Using CSV dataset: {len(csv_df):,} records")
                all_data.append(csv_df)
        except Exception as e:
            print(f"\n! CSV loading failed: {e}")
            
    # 2. Fetch from live APIs (skip if CSV data is very recent)
    api_start = start_year
    skip_api = False
    
    if use_csv_dataset and all_data:
        try:
            latest_date = all_data[0]['date'].max()
            # If CSV has data within last 3 days, skip expensive API fetching for dashboard speed
            if (datetime.now() - latest_date).days < 3:
                skip_api = True
            
            latest_csv_year = latest_date.year
            api_start = max(start_year, latest_csv_year)
        except:
            api_start = max(start_year, datetime.now().year - 1)
            
    if not skip_api:
        try:
            from src.unified_api_data_fetcher import fetch_unified_api_data, convert_to_pakpulse_format
            
            print("=" * 60)
            print(f"Fetching Unified Data from Multiple APIs ({api_start}-{end_year})")
            print("=" * 60)
            
            # Fetch unified data from all sources
            unified_df = fetch_unified_api_data(start_year=api_start, end_year=end_year)
            
            if not unified_df.empty:
                pakpulse_api = convert_to_pakpulse_format(unified_df)
                if not pakpulse_api.empty:
                    all_data.append(pakpulse_api)
                    print(f"\n* Using API data: {len(pakpulse_api):,} records")
        except Exception as e:
            print(f"Error fetching live API data: {e}")
        
    if not all_data:
        return pd.DataFrame(columns=["district", "latitude", "longitude", "disease", 
                                     "risk_index", "date", "cases_reported", "population"])
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Ensure consistent date format
    if 'date' in combined_df.columns:
        combined_df['date'] = pd.to_datetime(combined_df['date'])
    
    # Remove duplicates (prefer newer API data)
    combined_df = combined_df.drop_duplicates(
        subset=['district', 'disease', 'date'],
        keep='last'
    )
    
    return combined_df.sort_values(['district', 'disease', 'date'])

def _load_combined_api_data_fallback(start_year: int = 2015, end_year: int = 2025) -> pd.DataFrame:
    """
    Fallback method if unified fetcher fails
    NOTE: Only returns API data - no estimated data
    """
    # Try to fetch WHO data directly as fallback
    all_dataframes = []
    
    # Try WHO API directly
    try:
        from src.who_api import get_who_data_for_multiple_diseases
        who_df = get_who_data_for_multiple_diseases(["malaria", "cholera", "influenza"], "PAK")
        if not who_df.empty:
            all_dataframes.append(who_df)
    except:
        pass
    
    # Try Disease.sh API for COVID-19
    try:
        from src.disease_sh_api import get_disease_sh_data_all
        disease_sh_df = get_disease_sh_data_all()
        if not disease_sh_df.empty:
            all_dataframes.append(disease_sh_df)
    except:
        pass
    
    if all_dataframes:
        return pd.concat(all_dataframes, ignore_index=True)
    else:
        # Return empty DataFrame if no API data available
        # NO ESTIMATED DATA - only real API data
        return pd.DataFrame(columns=["district", "latitude", "longitude", "disease", 
                                     "risk_index", "date", "cases_reported", "population"])

def _convert_gdelt_to_standard_format(gdelt_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert GDELT DataFrame to standard PakPulse format
    
    Args:
        gdelt_df: DataFrame from GDELT with columns: ["title", "seendate", "domain", "url"]
        
    Returns:
        DataFrame in standard format
    """
    if gdelt_df.empty:
        return pd.DataFrame()
    
    # Load districts metadata
    loader = DataLoader(use_api=False, use_who=False)
    try:
        districts_meta = loader.load_districts_metadata()
    except:
        districts_meta = pd.DataFrame({
            "district": ["Karachi", "Lahore", "Islamabad"],
            "latitude": [24.8607, 31.5204, 33.6844],
            "longitude": [67.0011, 74.3587, 73.0479]
        })
    
    # Create mapping
    district_coords = {}
    for _, row in districts_meta.iterrows():
        district_coords[row['district']] = (row['latitude'], row['longitude'])
    
    # Convert GDELT data
    standard_data = []
    disease_keywords = {
        "dengue": "dengue",
        "malaria": "malaria",
        "cholera": "cholera",
        "influenza": "influenza",
        "flu": "influenza",
        "covid": "covid19",
        "coronavirus": "covid19"
    }
    
    for _, row in gdelt_df.iterrows():
        title = str(row.get('title', '')).lower()
        date_str = row.get('seendate', '')
        
        # Try to identify disease from title
        disease = "unknown"
        for keyword, disease_name in disease_keywords.items():
            if keyword in title:
                disease = disease_name
                break
        
        # Use first available district (GDELT doesn't provide specific location)
        district = list(district_coords.keys())[0] if district_coords else "Pakistan"
        lat, lon = district_coords.get(district, (30.3753, 69.3451))
        
        # Parse date
        try:
            date = pd.to_datetime(date_str)
        except:
            date = datetime.now()
        
        # Estimate risk based on news presence
        risk_index = 40  # Medium risk for news events
        
        standard_data.append({
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "disease": disease,
            "risk_index": risk_index,
            "date": date,
            "cases_reported": 1,  # Default, news doesn't provide exact counts
            "population": None
        })
    
    return pd.DataFrame(standard_data)

def _convert_nih_to_standard_format(nih_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert NIH DataFrame to standard PakPulse format
    
    Args:
        nih_df: DataFrame from NIH parser with columns: ["district", "disease", "cases", "week"]
        
    Returns:
        DataFrame in standard format: ["district", "latitude", "longitude", "disease", "risk_index", "date", "cases_reported"]
    """
    if nih_df.empty:
        return pd.DataFrame()
    
    # Load districts metadata for coordinates
    loader = DataLoader(use_api=False, use_who=False)
    districts_meta = loader.load_districts_metadata()
    
    # Create mapping
    district_coords = {}
    for _, row in districts_meta.iterrows():
        district_coords[row['district']] = (row['latitude'], row['longitude'])
    
    # Convert NIH data
    standard_data = []
    for _, row in nih_df.iterrows():
        district = row['district']
        disease = row['disease']
        cases = row['cases']
        week = row['week']
        
        # Get coordinates
        if district in district_coords:
            lat, lon = district_coords[district]
        else:
            # Use default coordinates if district not found
            lat, lon = 30.3753, 69.3451  # Pakistan center
        
        # Convert week to date (simplified - use week start)
        try:
            if 'W' in week:
                year, week_num = week.split('-W')
                # Approximate date (first day of week)
                date = datetime(int(year), 1, 1)
                week_offset = (int(week_num) - 1) * 7
                date = date.replace(day=1) + pd.Timedelta(days=week_offset)
            else:
                date = datetime.now()
        except:
            date = datetime.now()
        
        # Convert cases to risk_index (simple scaling)
        risk_index = min(100, max(0, (cases / 100) * 10)) if cases > 0 else 0
        
        standard_data.append({
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "disease": disease,
            "risk_index": int(risk_index),
            "date": date,
            "cases_reported": int(cases),
            "population": None
        })
    
    return pd.DataFrame(standard_data)

def _convert_healthmap_to_standard_format(healthmap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert HealthMap DataFrame to standard PakPulse format
    
    Args:
        healthmap_df: DataFrame from HealthMap with columns: ["disease", "location", "date", "summary"]
        
    Returns:
        DataFrame in standard format
    """
    if healthmap_df.empty:
        return pd.DataFrame()
    
    # Load districts metadata
    loader = DataLoader(use_api=False, use_who=False)
    districts_meta = loader.load_districts_metadata()
    
    # Create mapping
    district_coords = {}
    for _, row in districts_meta.iterrows():
        district_coords[row['district']] = (row['latitude'], row['longitude'])
    
    # Convert HealthMap data
    standard_data = []
    for _, row in healthmap_df.iterrows():
        location = row['location']
        disease = row['disease']
        date_str = row['date']
        summary = row.get('summary', '')
        
        # Try to match location to district
        district = location
        if location not in district_coords:
            # Try to find matching district
            for dist in district_coords.keys():
                if dist.lower() in location.lower() or location.lower() in dist.lower():
                    district = dist
                    break
        
        # Get coordinates
        if district in district_coords:
            lat, lon = district_coords[district]
        else:
            lat, lon = 30.3753, 69.3451  # Pakistan center
        
        # Parse date
        try:
            date = pd.to_datetime(date_str)
        except:
            date = datetime.now()
        
        # Estimate cases from summary (if available) or use default
        cases = 1  # Default, can be enhanced to extract from summary
        
        # Risk index based on alert presence
        risk_index = 50  # Medium risk for alerts
        
        standard_data.append({
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "disease": disease,
            "risk_index": risk_index,
            "date": date,
            "cases_reported": cases,
            "population": None
        })
    
    return pd.DataFrame(standard_data)

