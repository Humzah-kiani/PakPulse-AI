"""
WHO GHO API Integration Module for PakPulse AI
Fetches disease data from WHO Global Health Observatory API
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

# WHO GHO API Base URL
WHO_API_BASE = "https://ghoapi.azureedge.net/api"

# Common WHO indicator codes for diseases (actual codes from WHO GHO API)
WHO_INDICATORS = {
    "malaria": "MALARIA_CONF_CASES",  # Number of confirmed malaria cases
    "cholera": "CHOLERA_0000000001",  # Number of reported cases of cholera
    "influenza": "WHS3_51",  # H5N1 influenza - number of reported cases
    "tuberculosis": "TB",  # Using TB endpoint directly (as per user request)
    "meningitis": "MENINGITIS",  # Using MENINGITIS endpoint directly (as per user request)
    "hepatitis_a": "Hep_A",  # WHO Hepatitis A endpoint (as per user request)
    "hepatitis_e": "HEPATITISE",  # WHO Hepatitis E endpoint (as per user request)
    "covid19": None,  # COVID-19 data may be in different API
    "dengue": None  # Dengue data may not be available in WHO GHO
}

def get_who_disease_data(indicator: str = "MALARIA_CONF_CASES", country: str = "PAK") -> pd.DataFrame:
    """
    Fetch disease data from WHO GHO API
    
    Args:
        indicator: WHO indicator code (e.g., "MALARIA_CONF_CASES", "CHOLERA_0000000001")
        country: Country code (default: "PAK" for Pakistan)
        
    Returns:
        DataFrame with disease data
    """
    # WHO GHO API uses OData filter syntax
    url = f"{WHO_API_BASE}/{indicator}?$format=json&$filter=SpatialDim eq '{country}'"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json().get("value", [])
        
        if not data:
            print(f"Warning: No data found for indicator {indicator} in country {country}")
            return pd.DataFrame()
        
        # Map indicator codes to disease names
        disease_map = {
            "MALARIA_CONF_CASES": "malaria",
            "CHOLERA_0000000001": "cholera",
            "WHS3_51": "influenza",
            "TB": "tuberculosis",
            "TB_c_newinc": "tuberculosis",
            "TB_c_notified": "tuberculosis",
            "TB_e_inc_num": "tuberculosis",
            "WHS3_522": "tuberculosis",
            "MENINGITIS": "meningitis",
            "MENING_2": "meningitis",
            "MENING_1": "meningitis",
            "WHS3_47": "meningitis",
            "Hep_A": "hepatitis_a",
            "HEPATITISE": "hepatitis_e"
        }
        
        disease_name = disease_map.get(indicator, indicator.lower().replace("_conf_cases", "").replace("_0000000001", "").replace("whs3_51", "influenza").replace("tb_c_newinc", "tuberculosis").replace("tb_c_notified", "tuberculosis").replace("mening_2", "meningitis").replace("mening_1", "meningitis"))
        
        df = pd.DataFrame([
            {
                "disease": disease_name,
                "country": d.get("SpatialDim", country),
                "year": d.get("TimeDim"),
                "value": d.get("NumericValue") or d.get("Value", 0)  # Use NumericValue if available
            }
            for d in data if (d.get("NumericValue") is not None or d.get("Value") is not None)
        ])
        
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching WHO data: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing WHO data: {str(e)}")
        return pd.DataFrame()

def get_who_data_for_multiple_diseases(diseases: List[str] = None, country: str = "PAK") -> pd.DataFrame:
    """
    Fetch data for multiple diseases from WHO API
    
    Args:
        diseases: List of disease names (e.g., ["malaria", "cholera"])
        country: Country code (default: "PAK")
        
    Returns:
        Combined DataFrame with all disease data
    """
    if diseases is None:
        diseases = ["malaria", "cholera", "influenza", "tuberculosis", "meningitis"]
    
    all_data = []
    
    for disease in diseases:
        indicator = WHO_INDICATORS.get(disease.lower())
        if indicator:
            df = get_who_disease_data(indicator, country)
            if not df.empty:
                all_data.append(df)
        else:
            print(f"Warning: No WHO indicator found for disease: {disease}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def transform_who_data_to_risk_format(who_df: pd.DataFrame, 
                                     districts_metadata: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Transform WHO data format to match PakPulse risk data format
    
    Args:
        who_df: DataFrame from WHO API
        districts_metadata: Optional districts metadata for mapping
        
    Returns:
        DataFrame in PakPulse format (district, latitude, longitude, disease, risk_index, date)
    """
    if who_df.empty:
        return pd.DataFrame()
    
    # Load default districts if not provided
    if districts_metadata is None:
        try:
            from src.data_loader import DataLoader
            loader = DataLoader(use_api=False)
            districts_metadata = loader.load_districts_metadata()
        except:
            # Fallback: create basic district list
            districts_metadata = pd.DataFrame({
                "district": ["Karachi", "Lahore", "Islamabad"],
                "latitude": [24.8607, 31.5204, 33.6844],
                "longitude": [67.0011, 74.3587, 73.0479]
            })
    
    # Transform WHO data
    risk_data = []
    
    for _, who_row in who_df.iterrows():
        disease = who_row["disease"]
        year = who_row["year"]
        value = who_row["value"]
        
        # Map to each district (WHO data is country-level, so we distribute to districts)
        for _, district_row in districts_metadata.iterrows():
            # Convert WHO value to risk_index (0-100 scale)
            # This is a simple mapping - you may need to adjust based on actual WHO data ranges
            try:
                # Handle string values (e.g., "734 522" from WHO API)
                if isinstance(value, str):
                    # Remove spaces and convert
                    value = float(value.replace(" ", "").replace(",", ""))
                elif value is None:
                    value = 0
                else:
                    value = float(value)
                
                # Convert to risk index (simple scaling - adjust as needed)
                risk_index = min(100, max(0, (value / 1000) * 10)) if value > 0 else 0
            except (ValueError, TypeError):
                risk_index = 0
                value = 0
            
            # Create date (use year-end as default)
            date = datetime(int(year), 12, 31)
            
            risk_data.append({
                "district": district_row["district"],
                "latitude": district_row["latitude"],
                "longitude": district_row["longitude"],
                "disease": disease,
                "risk_index": int(risk_index),
                "date": date,
                "cases_reported": int(value) if value else 0,
                "population": None  # WHO data doesn't include population
            })
    
    return pd.DataFrame(risk_data)

