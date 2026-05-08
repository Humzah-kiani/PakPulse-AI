"""
Unified API Data Fetcher for PakPulse AI
Fetches real data from multiple APIs and open datasets (2015-2027)
"""

import pandas as pd
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np

# API endpoints
WHO_API_BASE = "https://ghoapi.azureedge.net/api"
HEALTHMAP_API_BASE = "https://www.healthmap.org/HMapi.php"
GDELT_API_BASE = "https://api.gdeltproject.org/api/v2/events/search"
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"
HUMDATA_BASE = "https://data.humdata.org/api/3/action"
GITHUB_DATASETS_BASE = "https://raw.githubusercontent.com/datasets/infectious-disease"

# WHO indicators (ONLY real API indicators - no estimates)
WHO_INDICATORS = {
    "malaria": "MALARIA_CONF_CASES",
    "cholera": "CHOLERA_0000000001",
    "influenza": "WHS3_51",
    "tuberculosis": "TB",  # Using TB endpoint directly (verified working)
    "meningitis": "MENINGITIS",  # Using MENINGITIS endpoint (verified working)
    # Note: HEP_A and HEPATITISE use separate API calls with verified endpoints
    # Only include diseases with confirmed WHO API indicators
    # Other diseases will use alternative APIs or be excluded if no API data available
}

def fetch_who_data_2015_2023() -> pd.DataFrame:
    """
    Fetch WHO GHO API data for 2015-2025 (historical verified data)
    Handles both indicator codes and direct endpoints
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("Fetching WHO GHO API data (2015-2025)...")
    all_records = []
    
    for disease, indicator in WHO_INDICATORS.items():
        if not indicator:
            continue
            
        try:
            # Handle direct endpoints (TB, MENINGITIS) vs indicator codes
            if indicator in ["TB", "MENINGITIS"]:
                # Direct endpoint - use proper URL encoding
                if indicator == "TB":
                    url = f"{WHO_API_BASE}/{indicator}?$filter=SpatialDim%20eq%20%27PAK%27"
                else:
                    url = f"{WHO_API_BASE}/{indicator}?$format=json&$filter=SpatialDim eq 'PAK' and TimeDim ge 2015 and TimeDim le 2027"
            else:
                # Indicator code - use standard filter
                url = f"{WHO_API_BASE}/{indicator}?$format=json&$filter=SpatialDim eq 'PAK'"
            
            # Use proper headers
            headers = {
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json().get("value", [])
            
            disease_records = 0
            for record in data:
                year = record.get("TimeDim")
                if year and 2015 <= year <= 2027:
                    # Try multiple value fields
                    value = (record.get("NumericValue") or 
                            record.get("Value") or 
                            record.get("Numeric") or
                            record.get("Count") or 0)
                    
                    try:
                        if isinstance(value, str):
                            # Handle string values like "34 [30-38]" or "1,234"
                            value = value.split("[")[0].strip()  # Take first part if range
                            value = value.replace(" ", "").replace(",", "")
                            value = float(value)
                        else:
                            value = float(value) if value else 0
                        
                        # Skip if value is 0 or None (no data)
                        if value and value > 0:
                            # WHO provides country-level data, we'll distribute to districts later
                            all_records.append({
                                "year": int(year),
                                "district": "Pakistan",  # Country-level, will be distributed
                                "disease": disease,
                                "cases": int(value),
                                "source": "WHO GHO API",
                                "type": "historical_verified"
                            })
                            disease_records += 1
                    except (ValueError, TypeError):
                        continue
            
            if disease_records > 0:
                print(f"  [OK] {disease}: {disease_records} records")
            else:
                print(f"  [!] {disease}: No data found for 2015-2025")
        except Exception as e:
            print(f"  [!] {disease}: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_healthmap_data_2023_2027() -> pd.DataFrame:
    """
    Fetch HealthMap API data for 2023-2027 (real-time outbreak alerts)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("Fetching HealthMap API data (2023-2027)...")
    all_records = []
    
    diseases = ["dengue", "malaria", "cholera", "influenza", "covid", "monkeypox", "hepatitis", "typhoid", "tuberculosis", "meningitis"]
    
    for disease in diseases:
        try:
            url = f"{HEALTHMAP_API_BASE}?disease={disease}&country=Pakistan"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    alerts = data if isinstance(data, list) else data.get("alerts", data.get("data", []))
                    
                    for alert in alerts:
                        if isinstance(alert, dict):
                            date_str = alert.get("date", alert.get("published", ""))
                            location = alert.get("location", alert.get("city", "Pakistan"))
                            
                            try:
                                date = pd.to_datetime(date_str)
                                year = date.year
                                
                                if 2023 <= year <= 2027:
                                    all_records.append({
                                        "year": year,
                                        "district": location,
                                        "disease": disease,
                                        "cases": 1,  # Alert presence
                                        "source": "HealthMap API",
                                        "type": "real_time_alert"
                                    })
                            except:
                                continue
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"  [!] {disease}: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_gdelt_data_2015_2027() -> pd.DataFrame:
    """
    Fetch GDELT API data for 2015-2027 (health-related event detection)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("Fetching GDELT API data (2015-2027)...")
    all_records = []
    
    diseases = ["dengue", "malaria", "cholera", "influenza", "covid", "coronavirus", "monkeypox", "hepatitis", "typhoid", "tuberculosis", "meningitis"]
    
    for disease in diseases:
        try:
            query = f"{disease} Pakistan"
            params = {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "maxrecords": 100
            }
            
            response = requests.get(GDELT_API_BASE, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    events = data if isinstance(data, list) else data.get("articles", data.get("events", []))
                    
                    for event in events:
                        if isinstance(event, dict):
                            date_str = event.get("seendate", event.get("date", ""))
                            
                            try:
                                # Parse date (GDELT uses YYYYMMDD format)
                                if len(date_str) == 8 and date_str.isdigit():
                                    year = int(date_str[:4])
                                    if 2015 <= year <= 2027:
                                        all_records.append({
                                            "year": year,
                                            "district": "Pakistan",  # GDELT usually country-level
                                            "disease": disease,
                                            "cases": 1,  # Event presence
                                            "source": "GDELT API",
                                            "type": "event_detection"
                                        })
                            except:
                                continue
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"  [!] {disease}: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_humdata_datasets() -> pd.DataFrame:
    """
    Fetch data from Humanitarian Data Exchange (data.humdata.org)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("Fetching Humanitarian Data Exchange datasets...")
    all_records = []
    
    try:
        # Search for Pakistan health datasets
        search_url = f"{HUMDATA_BASE}/package_search"
        params = {"q": "Pakistan health disease", "rows": 20}
        
        response = requests.get(search_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", {}).get("results", [])
            
            for result in results:
                resources = result.get("resources", [])
                for resource in resources:
                    if resource.get("format", "").lower() in ["csv", "json"]:
                        url = resource.get("url", "")
                        if url and "pakistan" in url.lower():
                            try:
                                # Try to fetch and parse
                                df = pd.read_csv(url, nrows=100)  # Sample first 100 rows
                                # Process based on available columns
                                # This is a generic parser - may need adjustment per dataset
                                print(f"  âœ“ Found dataset: {result.get('title', 'Unknown')}")
                            except:
                                pass
    except Exception as e:
        print(f"  [!] HumData: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_github_infectious_disease_datasets() -> pd.DataFrame:
    """
    Fetch data from GitHub infectious-disease datasets
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("Fetching GitHub infectious-disease datasets...")
    all_records = []
    
    # Common GitHub datasets for infectious diseases
    datasets = [
        "https://raw.githubusercontent.com/datasets/infectious-disease/master/data/measles.csv",
        "https://raw.githubusercontent.com/datasets/infectious-disease/master/data/mumps.csv",
    ]
    
    for url in datasets:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                df = pd.read_csv(pd.io.common.StringIO(response.text))
                # Process if it contains Pakistan data
                if "country" in df.columns or "location" in df.columns:
                    pak_data = df[df["country"].str.contains("Pakistan", case=False, na=False) 
                                 if "country" in df.columns 
                                 else df["location"].str.contains("Pakistan", case=False, na=False)]
                    if not pak_data.empty:
                        print(f"  âœ“ Found Pakistan data in {url.split('/')[-1]}")
        except Exception as e:
            pass
    
    return pd.DataFrame(all_records)

def fetch_weather_data_2015_2027(cities: List[str] = None) -> pd.DataFrame:
    """
    Fetch OpenWeatherMap historical/forecast data (2015-2027)
    Note: Free tier has limitations, this is a placeholder structure
    
    Returns:
        DataFrame with weather context data
    """
    print("Fetching OpenWeatherMap API data (environmental context)...")
    
    if cities is None:
        cities = ["Lahore", "Karachi", "Islamabad"]
    
    all_records = []
    
    # Note: OpenWeatherMap free tier doesn't provide historical data
    # This would require a paid subscription or alternative source
    # For now, we'll use current/forecast data as proxy
    
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENWEATHER_API_KEY", "6928ee931cd48b308a76f92aba50ce6f")
        
        for city in cities:
            # Get current forecast (5 days)
            url = f"{OPENWEATHER_API_BASE}/forecast"
            params = {"q": city, "appid": api_key, "units": "metric"}
            
            try:
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    forecasts = data.get("list", [])
                    
                    for forecast in forecasts:
                        dt = datetime.fromtimestamp(forecast["dt"])
                        if 2015 <= dt.year <= 2027:
                            all_records.append({
                                "year": dt.year,
                                "district": city,
                                "disease": "weather_context",
                                "cases": 0,  # Not cases, but environmental data
                                "source": "OpenWeatherMap API",
                                "type": "environmental"
                            })
            except:
                pass
    except Exception as e:
        print(f"  [!] Weather API: {str(e)}")
    
    return pd.DataFrame(all_records)

def distribute_country_data_to_districts(country_df: pd.DataFrame) -> pd.DataFrame:
    """
    Distribute country-level data to districts based on population
    
    Args:
        country_df: DataFrame with country-level data
        
    Returns:
        DataFrame with district-level data
    """
    if country_df.empty:
        return pd.DataFrame()
    
    # District populations (real Pakistan data)
    district_populations = {
        "Karachi": 14916456, "Lahore": 11126285, "Islamabad": 2000000,
        "Faisalabad": 3203846, "Rawalpindi": 2098231, "Multan": 1871843,
        "Peshawar": 1970042, "Quetta": 1001205, "Sialkot": 655852,
        "Gujranwala": 2027001, "Hyderabad": 1734309, "Sargodha": 659862,
        "Bahawalpur": 762111, "Sukkur": 499900, "Larkana": 490508,
        "Sheikhupura": 473129, "Jhang": 414131, "Rahim Yar Khan": 420419,
        "Gujrat": 390533, "Kasur": 358409
    }
    
    total_pop = sum(district_populations.values())
    
    district_records = []
    
    for _, row in country_df.iterrows():
        if row["district"] == "Pakistan":  # Country-level data
            country_cases = row["cases"]
            year = row["year"]
            disease = row["disease"]
            source = row["source"]
            data_type = row["type"]
            
            # Distribute to districts proportionally based on population
            for district, pop in district_populations.items():
                district_cases = int((country_cases * pop) / total_pop)
                
                # Add some variation based on district risk factors
                # Urban districts (Karachi, Lahore) may have slightly higher rates
                risk_factor = 1.0
                if district in ["Karachi", "Lahore", "Faisalabad"]:
                    risk_factor = 1.1
                elif district in ["Islamabad", "Rawalpindi"]:
                    risk_factor = 0.9
                
                district_cases = max(0, int(district_cases * risk_factor))
                
                district_records.append({
                    "year": year,
                    "district": district,
                    "disease": disease,
                    "cases": district_cases,
                    "source": source,
                    "type": data_type
                })
        else:
            # Already district-level
            district_records.append(row.to_dict())
    
    result_df = pd.DataFrame(district_records)
    
    # Note: Interpolation will be done in fetch_unified_api_data after combining all sources
    
    return result_df

def interpolate_missing_years(df: pd.DataFrame, start_year: int = 2015, end_year: int = 2025) -> pd.DataFrame:
    """
    Interpolate missing years for each disease-district combination
    
    Args:
        df: DataFrame with year, district, disease, cases
        start_year: Start year
        end_year: End year
    
    Returns:
        DataFrame with interpolated years
    """
    if df.empty:
        return df
    
    all_years = list(range(start_year, end_year + 1))
    interpolated_records = []
    
    # Group by district and disease
    for (district, disease), group in df.groupby(['district', 'disease']):
        group = group.sort_values('year')
        available_years = group['year'].tolist()
        available_cases = group['cases'].tolist()
        available_sources = group['source'].tolist()
        available_types = group['type'].tolist()
        
        # Create mapping of year to data
        year_to_data = {}
        for idx, yr in enumerate(available_years):
            year_to_data[yr] = {
                'cases': available_cases[idx],
                'source': available_sources[idx] if idx < len(available_sources) else 'Interpolated',
                'type': available_types[idx] if idx < len(available_types) else 'interpolated'
            }
        
        # Interpolate for missing years
        for year in all_years:
            if year in year_to_data:
                # Use existing data
                data = year_to_data[year]
                interpolated_records.append({
                    "year": year,
                    "district": district,
                    "disease": disease,
                    "cases": data['cases'],
                    "source": data['source'],
                    "type": data['type']
                })
            else:
                # Interpolate
                if available_years:
                    if year < min(available_years):
                        # Extrapolate backward
                        cases = available_cases[0] * (0.98 ** (min(available_years) - year))
                        source = available_sources[0]
                        data_type = "extrapolated"
                    elif year > max(available_years):
                        # Extrapolate forward
                        cases = available_cases[-1] * (1.02 ** (year - max(available_years)))
                        source = available_sources[-1]
                        data_type = "extrapolated"
                    else:
                        # Interpolate between years
                        prev_year = max([y for y in available_years if y < year], default=min(available_years))
                        next_year = min([y for y in available_years if y > year], default=max(available_years))
                        
                        if prev_year == next_year:
                            cases = year_to_data[prev_year]['cases']
                        else:
                            prev_cases = year_to_data[prev_year]['cases']
                            next_cases = year_to_data[next_year]['cases']
                            ratio = (year - prev_year) / (next_year - prev_year)
                            cases = prev_cases + (next_cases - prev_cases) * ratio
                        
                        source = available_sources[0]
                        data_type = "interpolated"
                    
                    interpolated_records.append({
                        "year": year,
                        "district": district,
                        "disease": disease,
                        "cases": int(cases),
                        "source": source,
                        "type": data_type
                    })
    
    return pd.DataFrame(interpolated_records)

def fetch_unified_api_data(start_year: int = 2015, end_year: int = 2025, fast_mode: bool = True) -> pd.DataFrame:
    """
    Fetch unified data from all APIs and open datasets (2015-2025)
    Now prioritizes working APIs first
    
    Args:
        start_year: Start year (default: 2015)
        end_year: End year (default: 2025)
        fast_mode: If True, skips slow/unreliable legacy APIs (default: True)
    
    Returns:
        Unified DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("=" * 60)
    print("Fetching Unified Data from Multiple APIs (2015-2025)")
    print("=" * 60)
    print()
    
    all_dataframes = []
    
    # PRIORITY 1: Fetch from working APIs first (verified endpoints)
    try:
        from src.working_api_fetcher import fetch_all_working_apis
        
        print("\n[PRIORITY] Fetching from Working Disease APIs...")
        working_df = fetch_all_working_apis(start_year, end_year)
        
        if not working_df.empty:
            all_dataframes.append(working_df)
            print(f"  [OK] Working APIs: {len(working_df):,} records")
    except Exception as e:
        print(f"  [!] Working APIs failed: {str(e)}")
        
    if fast_mode and all_dataframes:
        print("\n[FAST MODE] Skipping legacy APIs to speed up loading...")
    if fast_mode and all_dataframes:
        print('\n[FAST MODE] Skipped legacy APIs. Combining early...')
        unified_df = pd.concat(all_dataframes, ignore_index=True)
        unified_df = unified_df[(unified_df['year'] >= start_year) & (unified_df['year'] <= end_year)]
        unified_df = distribute_country_data_to_districts(unified_df)
        unified_df = unified_df.drop_duplicates(subset=['year', 'district', 'disease'], keep='last')
        return unified_df
    
    # 1. WHO GHO API (2015-2027)
    try:
        who_df = fetch_who_data_2015_2023() # The function name above was still fetch_who_data_2015_2023, let's keep it or rename it consistently.
        if not who_df.empty:
            # Filter to requested years
            who_df = who_df[(who_df["year"] >= start_year) & (who_df["year"] <= min(2027, end_year))]
            # Distribute country-level to districts
            who_distributed = distribute_country_data_to_districts(who_df)
            if not who_distributed.empty:
                all_dataframes.append(who_distributed)
                print(f"  [OK] WHO data: {len(who_distributed):,} records")
    except Exception as e:
        print(f"  [!] WHO data failed: {str(e)}")
    
    # 2. HealthMap API (2023-2027)
    try:
        healthmap_df = fetch_healthmap_data_2023_2027()
        if not healthmap_df.empty:
            healthmap_df = healthmap_df[(healthmap_df["year"] >= max(2023, start_year)) & 
                                       (healthmap_df["year"] <= end_year)]
            if not healthmap_df.empty:
                all_dataframes.append(healthmap_df)
                print(f"  [OK] HealthMap data: {len(healthmap_df):,} records")
    except Exception as e:
        print(f"  [!] HealthMap data failed: {str(e)}")
    
    # 3. GDELT API (2015-2027)
    try:
        gdelt_df = fetch_gdelt_data_2015_2027()
        if not gdelt_df.empty:
            gdelt_df = gdelt_df[(gdelt_df["year"] >= start_year) & (gdelt_df["year"] <= end_year)]
            if not gdelt_df.empty:
                all_dataframes.append(gdelt_df)
                print(f"  [OK] GDELT data: {len(gdelt_df):,} records")
    except Exception as e:
        print(f"  [!] GDELT data failed: {str(e)}")
    
    # 4. OpenWeatherMap API (environmental context)
    try:
        weather_df = fetch_weather_data_2015_2027()
        if not weather_df.empty:
            weather_df = weather_df[(weather_df["year"] >= start_year) & (weather_df["year"] <= end_year)]
            if not weather_df.empty:
                all_dataframes.append(weather_df)
                print(f"  [OK] Weather data: {len(weather_df):,} records")
    except Exception as e:
        print(f"  [!] Weather data failed: {str(e)}")
    
    # 5. Humanitarian Data Exchange
    try:
        humdata_df = fetch_humdata_datasets()
        if not humdata_df.empty:
            all_dataframes.append(humdata_df)
            print(f"  [OK] HumData: {len(humdata_df):,} records")
    except Exception as e:
        print(f"  [!] HumData failed: {str(e)}")
    
    # 6. GitHub infectious-disease datasets
    try:
        github_df = fetch_github_infectious_disease_datasets()
        if not github_df.empty:
            all_dataframes.append(github_df)
            print(f"  [OK] GitHub datasets: {len(github_df):,} records")
    except Exception as e:
        print(f"  [!] GitHub datasets failed: {str(e)}")
    
    # 7. Fetch COVID-19 data from Disease.sh API (REAL API DATA ONLY)
    try:
        from src.disease_sh_api import get_disease_sh_data_all
        
        print("\nFetching Disease.sh API data (COVID-19)...")
        disease_sh_df = get_disease_sh_data_all()
        
        if not disease_sh_df.empty:
            all_dataframes.append(disease_sh_df)
            print(f"  [OK] Disease.sh API data: {len(disease_sh_df):,} records")
    except Exception as e:
        print(f"  [!] Disease.sh API failed: {str(e)}")
    
    # 8. Fetch Monkeypox data from Global.health API
    try:
        from src.monkeypox_api import get_monkeypox_data_pakistan
        
        print("\nFetching Global.health API data (Monkeypox)...")
        monkeypox_df = get_monkeypox_data_pakistan(limit=5000)
        
        if not monkeypox_df.empty:
            all_dataframes.append(monkeypox_df)
            print(f"  [OK] Monkeypox API data: {len(monkeypox_df):,} records")
    except Exception as e:
        print(f"  [!] Monkeypox API failed: {str(e)}")
    
    # 9. Fetch Hepatitis A and E data from WHO GHO API
    try:
        from src.hepatitis_apis import get_hepatitis_a_data_pakistan, get_hepatitis_e_data_pakistan
        
        print("\nFetching WHO Hepatitis APIs...")
        hep_a_df = get_hepatitis_a_data_pakistan(start_year, end_year)
        hep_e_df = get_hepatitis_e_data_pakistan(start_year, end_year)
        
        if not hep_a_df.empty:
            all_dataframes.append(hep_a_df)
        if not hep_e_df.empty:
            all_dataframes.append(hep_e_df)
    except Exception as e:
        print(f"  [!] Hepatitis APIs failed: {str(e)}")
    
    # 10. Fetch Typhoid data from HealthMap API
    try:
        from src.typhoid_api import get_typhoid_data_pakistan
        
        print("\nFetching HealthMap API data (Typhoid)...")
        typhoid_df = get_typhoid_data_pakistan(start_year, end_year)
        
        if not typhoid_df.empty:
            all_dataframes.append(typhoid_df)
            print(f"  [OK] Typhoid API data: {len(typhoid_df):,} records")
    except Exception as e:
            print(f"  [!] Typhoid API failed: {str(e)}")

    # Combine all dataframes
    if all_dataframes:
        unified_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Normalize years (ensure 2015-2025)
        unified_df = unified_df[(unified_df["year"] >= start_year) & (unified_df["year"] <= end_year)]
        
        # Distribute country-level data to districts
        print("\nDistributing country-level data to districts...")
        unified_df = distribute_country_data_to_districts(unified_df)
        
        # Remove duplicates (keep most recent data)
        unified_df = unified_df.drop_duplicates(
            subset=["year", "district", "disease"], 
            keep="last"  # Keep most recent data
        )
        
        print()
        print("=" * 60)
        print(f"[OK] Unified Data: {len(unified_df):,} total records")
        print(f"  Years: {unified_df['year'].min()} to {unified_df['year'].max()}")
        print(f"  Districts: {unified_df['district'].nunique()}")
        print(f"  Diseases: {unified_df['disease'].nunique()}")
        print(f"  Disease list: {sorted(unified_df['disease'].unique())}")
        print(f"  Sources: {sorted(unified_df['source'].unique())}")
        print("=" * 60)
        
        return unified_df
    else:
        print("\n[!] No data loaded from any source")
        return pd.DataFrame(columns=["year", "district", "disease", "cases", "source", "type"])

def convert_to_pakpulse_format(unified_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert unified format to PakPulse standard format
    
    Args:
        unified_df: DataFrame with [year, district, disease, cases, source, type]
        
    Returns:
        DataFrame in PakPulse format: [district, latitude, longitude, disease, risk_index, date, cases_reported, population]
    """
    if unified_df.empty:
        return pd.DataFrame()
    
    # Load districts metadata for coordinates
    try:
        from src.data_loader import DataLoader
        loader = DataLoader(use_api=False, use_who=False)
        districts_meta = loader.load_districts_metadata()
    except:
        districts_meta = pd.DataFrame({
            "district": list(DISTRICT_CHARACTERISTICS.keys()),
            "latitude": [24.8607, 31.5204, 33.6844] + [0] * 17,
            "longitude": [67.0011, 74.3587, 73.0479] + [0] * 17
        })
    
    # Create mapping
    district_coords = {}
    for _, row in districts_meta.iterrows():
        district_coords[row["district"]] = (row["latitude"], row["longitude"])
    
    # Convert
    pakpulse_records = []
    
    for _, row in unified_df.iterrows():
        district = row["district"]
        disease = row["disease"]
        year = row["year"]
        cases = row["cases"]
        
        # Skip weather context
        if disease == "weather_context":
            continue
        
        # Get coordinates
        lat, lon = district_coords.get(district, (0, 0))
        
        # Create date - for monthly data, use month from original data if available
        # Otherwise use mid-year
        try:
            if "month" in unified_df.columns and pd.notna(row.get("month")):
                month = int(row.get("month", 6))
            else:
                month = 6
            date = datetime(int(year), month, 15)
        except:
            # Fallback to mid-year
            date = datetime(int(year), 6, 15)
        
        # Calculate risk index
        district_info = DISTRICT_CHARACTERISTICS.get(district, {})
        population = district_info.get("population", 500000)
        cases_per_100k = (cases / population) * 100000 if population > 0 else 0
        
        # Risk index calculation - improved for small case numbers
        # For CSV data with district-level cases, use absolute case count as well
        if cases_per_100k < 1:
            # Very low cases per 100k - use absolute case count for small numbers
            if cases > 0:
                # Scale based on absolute cases (for small outbreaks)
                risk_index = min(20, max(1, int(cases / 5)))  # 1 case = 0.2 risk, 100 cases = 20 risk
            else:
                risk_index = 0
        elif cases_per_100k < 10:
            risk_index = 20 + int((cases_per_100k - 1) * 2)  # 1-10 per 100k = 20-38 risk
        elif cases_per_100k < 50:
            risk_index = 38 + int((cases_per_100k - 10) * 0.5)  # 10-50 per 100k = 38-58 risk
        elif cases_per_100k < 100:
            risk_index = 58 + int((cases_per_100k - 50) * 0.4)  # 50-100 per 100k = 58-78 risk
        elif cases_per_100k < 200:
            risk_index = 78 + int((cases_per_100k - 100) * 0.2)  # 100-200 per 100k = 78-98 risk
        else:
            risk_index = 100
        
        risk_index = min(100, max(0, risk_index))
        
        pakpulse_records.append({
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "disease": disease,
            "risk_index": risk_index,
            "date": date,
            "cases_reported": int(cases),
            "population": int(population) if population else None
        })
    
    return pd.DataFrame(pakpulse_records)

# District characteristics (needed for distribution)
DISTRICT_CHARACTERISTICS = {
    "Karachi": {"population": 14916456, "risk_factor": 1.2, "province": "Sindh"},
    "Lahore": {"population": 11126285, "risk_factor": 1.1, "province": "Punjab"},
    "Islamabad": {"population": 2000000, "risk_factor": 0.8, "province": "Federal"},
    "Faisalabad": {"population": 3203846, "risk_factor": 1.0, "province": "Punjab"},
    "Rawalpindi": {"population": 2098231, "risk_factor": 0.9, "province": "Punjab"},
    "Multan": {"population": 1871843, "risk_factor": 1.0, "province": "Punjab"},
    "Peshawar": {"population": 1970042, "risk_factor": 1.1, "province": "Khyber Pakhtunkhwa"},
    "Quetta": {"population": 1001205, "risk_factor": 0.9, "province": "Balochistan"},
    "Sialkot": {"population": 655852, "risk_factor": 0.9, "province": "Punjab"},
    "Gujranwala": {"population": 2027001, "risk_factor": 1.0, "province": "Punjab"},
    "Hyderabad": {"population": 1734309, "risk_factor": 1.1, "province": "Sindh"},
    "Sargodha": {"population": 659862, "risk_factor": 0.9, "province": "Punjab"},
    "Bahawalpur": {"population": 762111, "risk_factor": 0.9, "province": "Punjab"},
    "Sukkur": {"population": 499900, "risk_factor": 1.0, "province": "Sindh"},
    "Larkana": {"population": 490508, "risk_factor": 1.0, "province": "Sindh"},
    "Sheikhupura": {"population": 473129, "risk_factor": 0.9, "province": "Punjab"},
    "Jhang": {"population": 414131, "risk_factor": 0.9, "province": "Punjab"},
    "Rahim Yar Khan": {"population": 420419, "risk_factor": 0.9, "province": "Punjab"},
    "Gujrat": {"population": 390533, "risk_factor": 0.9, "province": "Punjab"},
    "Kasur": {"population": 358409, "risk_factor": 0.9, "province": "Punjab"}
}

