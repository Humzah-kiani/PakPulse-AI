"""
Comprehensive Real-World Data Generator for PakPulse AI
Generates realistic district-level disease data (2015-2025) based on real WHO patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Real WHO data patterns (will be fetched from API)
WHO_API_BASE = "https://ghoapi.azureedge.net/api"

# All diseases to generate (11 total)
ALL_DISEASES = [
    "dengue", "malaria", "cholera", "influenza", "covid19",
    "monkeypox", "hepatitis_a", "hepatitis_e", "typhoid", "tuberculosis", "meningitis"
]

# District characteristics (based on real Pakistan data)
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

def fetch_real_who_baseline() -> Dict:
    """
    Fetch real WHO data to use as baseline for generating realistic data
    
    Returns:
        Dictionary with disease baselines from WHO
    """
    baselines = {}
    
    # Fetch malaria data
    try:
        url = f"{WHO_API_BASE}/MALARIA_CONF_CASES?$format=json&$filter=SpatialDim eq 'PAK'"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json().get("value", [])
            if data:
                # Get latest year's data
                latest = max(data, key=lambda x: x.get("TimeDim", 0))
                baselines["malaria"] = {
                    "latest_value": float(str(latest.get("NumericValue", 0)).replace(" ", "").replace(",", "") or 0),
                    "latest_year": latest.get("TimeDim"),
                    "all_years": {d.get("TimeDim"): float(str(d.get("NumericValue", 0)).replace(" ", "").replace(",", "") or 0) 
                                 for d in data if d.get("NumericValue")}
                }
    except:
        baselines["malaria"] = {"latest_value": 2743659, "latest_year": 2023, "all_years": {}}
    
    # Fetch cholera data
    try:
        url = f"{WHO_API_BASE}/CHOLERA_0000000001?$format=json&$filter=SpatialDim eq 'PAK'"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json().get("value", [])
            if data:
                latest = max(data, key=lambda x: x.get("TimeDim", 0))
                baselines["cholera"] = {
                    "latest_value": float(str(latest.get("NumericValue", 0)).replace(" ", "").replace(",", "") or 0),
                    "latest_year": latest.get("TimeDim"),
                    "all_years": {d.get("TimeDim"): float(str(d.get("NumericValue", 0)).replace(" ", "").replace(",", "") or 0) 
                                 for d in data if d.get("NumericValue")}
                }
    except:
        baselines["cholera"] = {"latest_value": 5000, "latest_year": 2023, "all_years": {}}
    
    # Set defaults for diseases not in WHO
    if "dengue" not in baselines:
        baselines["dengue"] = {"latest_value": 50000, "latest_year": 2023, "all_years": {}}
    if "influenza" not in baselines:
        baselines["influenza"] = {"latest_value": 100000, "latest_year": 2023, "all_years": {}}
    if "covid19" not in baselines:
        baselines["covid19"] = {"latest_value": 1500000, "latest_year": 2023, "all_years": {}}
    
    return baselines

def generate_comprehensive_data(start_year: int = 2015, end_year: int = 2025, 
                                frequency: str = "weekly") -> pd.DataFrame:
    """
    Generate comprehensive realistic disease data for all districts and diseases (2015-2025)
    Based on real WHO patterns
    
    Args:
        start_year: Start year (default: 2015)
        end_year: End year (default: 2025)
        frequency: "weekly" or "monthly" (default: "weekly")
        
    Returns:
        DataFrame with comprehensive disease data
    """
    print("Generating comprehensive disease data (2015-2025)...")
    print("Fetching real WHO baseline data...")
    
    # Fetch real WHO baselines
    baselines = fetch_real_who_baseline()
    
    # Load districts metadata
    try:
        from src.data_loader import DataLoader
        loader = DataLoader(use_api=False, use_who=False)
        districts_meta = loader.load_districts_metadata()
    except:
        # Fallback to hardcoded districts
        districts_meta = pd.DataFrame([
            {"district": dist, "latitude": 0, "longitude": 0, "province": info["province"]}
            for dist, info in DISTRICT_CHARACTERISTICS.items()
        ])
    
    all_records = []
    
    # Generate dates
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    if frequency == "weekly":
        date_step = timedelta(days=7)
    else:
        date_step = timedelta(days=30)
    
    current_date = start_date
    total_weeks = 0
    
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        week_of_year = current_date.isocalendar()[1]
        
        # Get baseline for this year
        for disease in ALL_DISEASES:
            baseline_info = baselines.get(disease, {})
            all_years = baseline_info.get("all_years", {})
            
            # Get value for this year if available, otherwise interpolate
            if year in all_years:
                country_cases = all_years[year]
            elif all_years:
                # Interpolate based on available years
                available_years = sorted(all_years.keys())
                if year < min(available_years):
                    country_cases = all_years[min(available_years)] * 0.8
                elif year > max(available_years):
                    country_cases = all_years[max(available_years)] * 1.1
                else:
                    # Find closest years
                    prev_year = max([y for y in available_years if y < year], default=min(available_years))
                    next_year = min([y for y in available_years if y > year], default=max(available_years))
                    if prev_year == next_year:
                        country_cases = all_years[prev_year]
                    else:
                        # Linear interpolation
                        ratio = (year - prev_year) / (next_year - prev_year)
                        country_cases = all_years[prev_year] * (1 - ratio) + all_years[next_year] * ratio
            else:
                # Use default with trend
                latest_value = baseline_info.get("latest_value", 10000)
                latest_year = baseline_info.get("latest_year", 2023)
                # Trend: increase 2% per year
                years_diff = year - latest_year
                country_cases = latest_value * (1.02 ** years_diff)
            
            # Seasonal factors (diseases peak at different times)
            seasonal_factor = get_seasonal_factor(disease, month)
            
            # Generate data for each district
            for _, district_row in districts_meta.iterrows():
                district = district_row["district"]
                district_info = DISTRICT_CHARACTERISTICS.get(district, {})
                
                # Calculate district cases based on population and risk factor
                district_population = district_info.get("population", 500000)
                risk_factor = district_info.get("risk_factor", 1.0)
                
                # Distribute country cases to districts (proportional to population with risk factor)
                total_pop = sum(DISTRICT_CHARACTERISTICS[d].get("population", 500000) 
                               for d in DISTRICT_CHARACTERISTICS.keys())
                population_share = district_population / total_pop
                
                # Weekly/monthly cases
                if frequency == "weekly":
                    cases = (country_cases * population_share * risk_factor * seasonal_factor) / 52
                else:
                    cases = (country_cases * population_share * risk_factor * seasonal_factor) / 12
                
                # Add some randomness (realistic variation)
                cases = max(0, int(cases * np.random.uniform(0.7, 1.3)))
                
                # Calculate risk index (0-100)
                # Based on cases per 100,000 population
                cases_per_100k = (cases / district_population) * 100000 if district_population > 0 else 0
                risk_index = calculate_risk_index(disease, cases_per_100k)
                
                all_records.append({
                    "district": district,
                    "latitude": district_row.get("latitude", 0),
                    "longitude": district_row.get("longitude", 0),
                    "disease": disease,
                    "risk_index": int(risk_index),
                    "date": current_date,
                    "cases_reported": int(cases),
                    "population": int(district_population)
                })
        
        current_date += date_step
        total_weeks += 1
        if total_weeks % 50 == 0:
            print(f"  Generated {total_weeks} weeks of data...")
    
    df = pd.DataFrame(all_records)
    print(f"\nâœ… Generated {len(df)} records")
    print(f"   Districts: {df['district'].nunique()}")
    print(f"   Diseases: {df['disease'].nunique()}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df

def get_seasonal_factor(disease: str, month: int) -> float:
    """
    Get seasonal factor for disease (some diseases peak in certain months)
    
    Args:
        disease: Disease name
        month: Month (1-12)
        
    Returns:
        Seasonal multiplier (0.5 to 1.5)
    """
    # Dengue: Peak in monsoon (July-September)
    if disease == "dengue":
        if month in [7, 8, 9]:
            return 1.5
        elif month in [6, 10]:
            return 1.2
        else:
            return 0.7
    
    # Malaria: Peak in summer (June-September)
    elif disease == "malaria":
        if month in [6, 7, 8, 9]:
            return 1.4
        elif month in [5, 10]:
            return 1.1
        else:
            return 0.8
    
    # Cholera: Peak in summer (May-September)
    elif disease == "cholera":
        if month in [5, 6, 7, 8, 9]:
            return 1.3
        else:
            return 0.9
    
    # Influenza: Peak in winter (December-February)
    elif disease == "influenza":
        if month in [12, 1, 2]:
            return 1.5
        elif month in [11, 3]:
            return 1.2
        else:
            return 0.8
    
    # COVID-19: Less seasonal, but higher in winter
    elif disease == "covid19":
        if month in [12, 1, 2]:
            return 1.2
        else:
            return 1.0
    
    return 1.0

def calculate_risk_index(disease: str, cases_per_100k: float) -> float:
    """
    Calculate risk index (0-100) based on cases per 100,000 population
    
    Args:
        disease: Disease name
        cases_per_100k: Cases per 100,000 population
        
    Returns:
        Risk index (0-100)
    """
    # Different thresholds for different diseases
    thresholds = {
        "dengue": {"low": 10, "moderate": 50, "high": 100, "very_high": 200},
        "malaria": {"low": 20, "moderate": 100, "high": 200, "very_high": 500},
        "cholera": {"low": 5, "moderate": 20, "high": 50, "very_high": 100},
        "influenza": {"low": 100, "moderate": 500, "high": 1000, "very_high": 2000},
        "covid19": {"low": 50, "moderate": 200, "high": 500, "very_high": 1000}
    }
    
    thresh = thresholds.get(disease, thresholds["dengue"])
    
    if cases_per_100k < thresh["low"]:
        # Linear from 0 to 20
        return min(20, (cases_per_100k / thresh["low"]) * 20)
    elif cases_per_100k < thresh["moderate"]:
        # Linear from 20 to 40
        return 20 + ((cases_per_100k - thresh["low"]) / (thresh["moderate"] - thresh["low"])) * 20
    elif cases_per_100k < thresh["high"]:
        # Linear from 40 to 60
        return 40 + ((cases_per_100k - thresh["moderate"]) / (thresh["high"] - thresh["moderate"])) * 20
    elif cases_per_100k < thresh["very_high"]:
        # Linear from 60 to 80
        return 60 + ((cases_per_100k - thresh["high"]) / (thresh["very_high"] - thresh["high"])) * 20
    else:
        # Linear from 80 to 100
        return min(100, 80 + ((cases_per_100k - thresh["very_high"]) / thresh["very_high"]) * 20)

def save_comprehensive_data(df: pd.DataFrame, output_dir: str = "data"):
    """
    Save comprehensive data to CSV and JSON files
    
    Args:
        df: DataFrame to save
        output_dir: Output directory
    """
    from pathlib import Path
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save CSV
    csv_path = output_path / "disease_risk_data_comprehensive.csv"
    df.to_csv(csv_path, index=False)
    print(f"âœ… Saved to {csv_path}")
    
    # Save JSON
    json_path = output_path / "disease_risk_data_comprehensive.json"
    df.to_json(json_path, orient="records", date_format="iso")
    print(f"âœ… Saved to {json_path}")
    
    return csv_path, json_path


