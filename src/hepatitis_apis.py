"""
WHO Hepatitis A and E API Integration for PakPulse AI
APIs:
- Hepatitis A: https://ghoapi.azureedge.net/api/Hep_A
- Hepatitis E: https://ghoapi.azureedge.net/api/HEPATITISE
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

WHO_API_BASE = "https://ghoapi.azureedge.net/api"

def get_hepatitis_a_data_pakistan(start_year: int = 2015, end_year: int = 2025) -> pd.DataFrame:
    """
    Fetch Hepatitis A data for Pakistan from WHO GHO API
    
    Args:
        start_year: Start year (default: 2015)
        end_year: End year (default: 2025)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        # Use verified working endpoint HEP_A
        url = f"{WHO_API_BASE}/HEP_A?$format=json&$filter=SpatialDim eq 'PAK' and TimeDim ge {start_year} and TimeDim le {end_year}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json().get("value", [])
        except:
            # Try alternative endpoint Hep_A (case variation)
            try:
                url = f"{WHO_API_BASE}/Hep_A?$format=json&$filter=SpatialDim eq 'PAK' and TimeDim ge {start_year} and TimeDim le {end_year}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json().get("value", [])
            except:
                data = []
        
        for record in data:
            year = record.get("TimeDim")
            if year and start_year <= year <= end_year:
                value = record.get("NumericValue") or record.get("Value", 0)
                try:
                    if isinstance(value, str):
                        value = value.split("[")[0].strip()
                        value = value.replace(" ", "").replace(",", "")
                        value = float(value)
                    else:
                        value = float(value)
                    
                    if value and value > 0:
                        all_records.append({
                            "year": int(year),
                            "district": "Pakistan",  # Country-level, will be distributed
                            "disease": "hepatitis_a",
                            "cases": int(value),
                            "source": "WHO GHO API",
                            "type": "historical_verified"
                        })
                except (ValueError, TypeError):
                    continue
        
        print(f"  âœ“ hepatitis_a: {len(all_records)} records")
        
    except Exception as e:
        print(f"  âš  hepatitis_a: {str(e)}")
    
    return pd.DataFrame(all_records)

def get_hepatitis_e_data_pakistan(start_year: int = 2015, end_year: int = 2025) -> pd.DataFrame:
    """
    Fetch Hepatitis E data for Pakistan from WHO GHO API
    
    Args:
        start_year: Start year (default: 2015)
        end_year: End year (default: 2025)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        # Use verified working endpoint HEPATITISE
        url = f"{WHO_API_BASE}/HEPATITISE?$format=json&$filter=SpatialDim eq 'PAK' and TimeDim ge {start_year} and TimeDim le {end_year}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json().get("value", [])
        
        for record in data:
            year = record.get("TimeDim")
            if year and start_year <= year <= end_year:
                value = record.get("NumericValue") or record.get("Value", 0)
                try:
                    if isinstance(value, str):
                        value = value.split("[")[0].strip()
                        value = value.replace(" ", "").replace(",", "")
                        value = float(value)
                    else:
                        value = float(value)
                    
                    if value and value > 0:
                        all_records.append({
                            "year": int(year),
                            "district": "Pakistan",  # Country-level, will be distributed
                            "disease": "hepatitis_e",
                            "cases": int(value),
                            "source": "WHO GHO API",
                            "type": "historical_verified"
                        })
                except (ValueError, TypeError):
                    continue
        
        print(f"  âœ“ hepatitis_e: {len(all_records)} records")
        
    except Exception as e:
        print(f"  âš  hepatitis_e: {str(e)}")
    
    return pd.DataFrame(all_records)

