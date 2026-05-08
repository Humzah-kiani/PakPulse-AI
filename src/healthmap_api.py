"""
HealthMap Real-Time Outbreak API Integration
Fetches real-time disease alerts from HealthMap
"""

import requests
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
import json

HEALTHMAP_API_BASE = "https://www.healthmap.org/HMapi.php"

def get_healthmap_alerts(disease: str = "dengue", country: str = "Pakistan") -> pd.DataFrame:
    """
    Fetch real-time disease alerts from HealthMap API
    
    Args:
        disease: Disease name (e.g., "dengue", "malaria", "cholera")
        country: Country name (default: "Pakistan")
        
    Returns:
        DataFrame with columns: ["disease", "location", "date", "summary"]
    """
    url = f"{HEALTHMAP_API_BASE}?disease={disease}&country={country}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # HealthMap API returns JSON
        data = response.json()
        
        if not data:
            print(f"Warning: No HealthMap alerts found for {disease} in {country}")
            return pd.DataFrame(columns=["disease", "location", "date", "summary"])
        
        # Parse HealthMap response format
        alerts = []
        
        # HealthMap may return different formats
        if isinstance(data, list):
            alerts_data = data
        elif isinstance(data, dict):
            # Check common keys
            if 'alerts' in data:
                alerts_data = data['alerts']
            elif 'data' in data:
                alerts_data = data['data']
            elif 'results' in data:
                alerts_data = data['results']
            else:
                # Try to extract from dict values
                alerts_data = [data]
        else:
            alerts_data = []
        
        for alert in alerts_data:
            if isinstance(alert, dict):
                alerts.append({
                    "disease": disease,
                    "location": alert.get("location", alert.get("city", alert.get("place", country))),
                    "date": _parse_healthmap_date(alert.get("date", alert.get("published", ""))),
                    "summary": alert.get("summary", alert.get("title", alert.get("description", "")))
                })
        
        if alerts:
            df = pd.DataFrame(alerts)
            return df
        else:
            print(f"Warning: No valid alerts parsed from HealthMap response")
            return pd.DataFrame(columns=["disease", "location", "date", "summary"])
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HealthMap data: {str(e)}")
        return pd.DataFrame(columns=["disease", "location", "date", "summary"])
    except json.JSONDecodeError as e:
        print(f"Error parsing HealthMap JSON: {str(e)}")
        # Try to parse as text/HTML if JSON fails
        return _parse_healthmap_text(response.text, disease, country)
    except Exception as e:
        print(f"Error processing HealthMap data: {str(e)}")
        return pd.DataFrame(columns=["disease", "location", "date", "summary"])

def _parse_healthmap_date(date_str: str) -> str:
    """
    Parse date string from HealthMap API
    
    Args:
        date_str: Date string from API
        
    Returns:
        Formatted date string (YYYY-MM-DD) or empty string
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Try various date formats
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                dt = datetime.strptime(date_str[:10], fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                continue
        return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

def _parse_healthmap_text(text: str, disease: str, country: str) -> pd.DataFrame:
    """
    Fallback parser if HealthMap returns text/HTML instead of JSON
    
    Args:
        text: Response text
        disease: Disease name
        country: Country name
        
    Returns:
        DataFrame with alerts
    """
    # Basic text parsing (can be enhanced)
    alerts = []
    
    # If text contains disease mentions, create a basic alert
    if disease.lower() in text.lower() and country.lower() in text.lower():
        alerts.append({
            "disease": disease,
            "location": country,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": f"HealthMap alert for {disease} in {country}"
        })
    
    if alerts:
        return pd.DataFrame(alerts)
    else:
        return pd.DataFrame(columns=["disease", "location", "date", "summary"])

def get_healthmap_alerts_multiple_diseases(diseases: List[str] = None, 
                                          country: str = "Pakistan") -> pd.DataFrame:
    """
    Fetch alerts for multiple diseases
    
    Args:
        diseases: List of disease names
        country: Country name
        
    Returns:
        Combined DataFrame with all alerts
    """
    if diseases is None:
        diseases = ["dengue", "malaria", "cholera", "influenza", "covid", "monkeypox", "hepatitis", "typhoid", "tuberculosis", "meningitis"]
    
    all_alerts = []
    
    for disease in diseases:
        df = get_healthmap_alerts(disease, country)
        if not df.empty:
            all_alerts.append(df)
    
    if all_alerts:
        return pd.concat(all_alerts, ignore_index=True)
    else:
        return pd.DataFrame(columns=["disease", "location", "date", "summary"])


