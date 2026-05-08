"""
Disease.sh API Integration for PakPulse AI
Provides real-time data for COVID-19, Influenza, and other diseases
API: https://disease.sh/
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

DISEASE_SH_API_BASE = "https://disease.sh/v3/covid-19"
DISEASE_SH_HISTORICAL = "https://disease.sh/v3/covid-19/historical"

def get_covid19_data_pakistan() -> pd.DataFrame:
    """
    Fetch COVID-19 data for Pakistan from Disease.sh API
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        # Get current COVID-19 data for Pakistan
        url = f"{DISEASE_SH_API_BASE}/countries/Pakistan"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data:
            # Get current date
            today = datetime.now()
            year = today.year
            
            # Current cases
            cases = data.get("cases", 0)
            active = data.get("active", 0)
            recovered = data.get("recovered", 0)
            deaths = data.get("deaths", 0)
            
            # Total cases is the most relevant
            total_cases = cases
            
            all_records.append({
                "year": year,
                "district": "Pakistan",  # Country-level
                "disease": "covid19",
                "cases": int(total_cases),
                "source": "Disease.sh API",
                "type": "real_time"
            })
            
    except Exception as e:
        print(f"  âš  COVID-19 (current): {str(e)}")
    
    # Try to get historical data
    try:
        url = f"{DISEASE_SH_HISTORICAL}/Pakistan"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data and "timeline" in data:
            timeline = data["timeline"]
            cases_timeline = timeline.get("cases", {})
            
            for date_str, cases in cases_timeline.items():
                try:
                    date = datetime.strptime(date_str, "%m/%d/%y")
                    year = date.year
                    
                    if 2015 <= year <= 2025:
                        all_records.append({
                            "year": year,
                            "district": "Pakistan",
                            "disease": "covid19",
                            "cases": int(cases),
                            "source": "Disease.sh API",
                            "type": "historical_verified"
                        })
                except:
                    continue
                    
    except Exception as e:
        print(f"  âš  COVID-19 (historical): {str(e)}")
    
    return pd.DataFrame(all_records)

def get_influenza_data() -> pd.DataFrame:
    """
    Try to get influenza data (Disease.sh may have limited data)
    
    Returns:
        DataFrame with influenza data if available
    """
    # Disease.sh primarily focuses on COVID-19
    # Influenza data may need to come from WHO or other sources
    return pd.DataFrame()

def get_disease_sh_data_all() -> pd.DataFrame:
    """
    Fetch all available data from Disease.sh API
    
    Returns:
        Combined DataFrame
    """
    all_dataframes = []
    
    # COVID-19
    try:
        covid_df = get_covid19_data_pakistan()
        if not covid_df.empty:
            all_dataframes.append(covid_df)
            print(f"  âœ“ COVID-19: {len(covid_df)} records from Disease.sh API")
    except Exception as e:
        print(f"  âš  Disease.sh API error: {str(e)}")
    
    # Combine
    if all_dataframes:
        return pd.concat(all_dataframes, ignore_index=True)
    return pd.DataFrame()



