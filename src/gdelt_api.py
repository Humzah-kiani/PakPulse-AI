"""
GDELT Event API Integration Module for PakPulse AI
Fetches real-time news events related to diseases in Pakistan
"""

import requests
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
import json

GDELT_API_BASE = "https://api.gdeltproject.org/api/v2/events/search"

def get_gdelt_health_events(query: str = "dengue Pakistan") -> pd.DataFrame:
    """
    Fetch real-time news events related to diseases in Pakistan from GDELT API
    
    Args:
        query: Search query (e.g., "dengue Pakistan", "malaria Pakistan")
        
    Returns:
        DataFrame with columns: ["title", "seendate", "domain", "url"]
    """
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": 50
    }
    
    try:
        response = requests.get(GDELT_API_BASE, params=params, timeout=30)
        response.raise_for_status()
        
        # GDELT API returns different formats
        try:
            data = response.json()
        except json.JSONDecodeError:
            # Try parsing as text
            text = response.text
            if not text or text.strip() == "":
                print(f"Warning: Empty response from GDELT API for query: {query}")
                return pd.DataFrame(columns=["title", "seendate", "domain", "url"])
            
            # Try to parse as JSON lines
            try:
                lines = text.strip().split('\n')
                data = [json.loads(line) for line in lines if line.strip()]
            except:
                print(f"Warning: Could not parse GDELT response for query: {query}")
                return pd.DataFrame(columns=["title", "seendate", "domain", "url"])
        
        if not data:
            print(f"Warning: No GDELT events found for query: {query}")
            return pd.DataFrame(columns=["title", "seendate", "domain", "url"])
        
        # Parse GDELT response format
        events = []
        
        # GDELT may return different formats
        if isinstance(data, list):
            events_data = data
        elif isinstance(data, dict):
            if 'articles' in data:
                events_data = data['articles']
            elif 'events' in data:
                events_data = data['events']
            elif 'results' in data:
                events_data = data['results']
            else:
                events_data = [data]
        else:
            events_data = []
        
        for event in events_data:
            if isinstance(event, dict):
                # Extract relevant fields
                title = event.get("title", event.get("snippet", event.get("summary", "")))
                seendate = event.get("seendate", event.get("date", event.get("datetime", "")))
                domain = event.get("domain", event.get("source", event.get("sourcedomain", "")))
                url = event.get("url", event.get("link", event.get("articleurl", "")))
                
                if title:  # Only add if we have at least a title
                    events.append({
                        "title": title,
                        "seendate": _parse_gdelt_date(seendate),
                        "domain": domain,
                        "url": url
                    })
        
        if events:
            df = pd.DataFrame(events)
            return df
        else:
            print(f"Warning: No valid events parsed from GDELT response")
            return pd.DataFrame(columns=["title", "seendate", "domain", "url"])
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GDELT data: {str(e)}")
        return pd.DataFrame(columns=["title", "seendate", "domain", "url"])
    except Exception as e:
        print(f"Error processing GDELT data: {str(e)}")
        return pd.DataFrame(columns=["title", "seendate", "domain", "url"])

def _parse_gdelt_date(date_str: str) -> str:
    """
    Parse date string from GDELT API
    
    Args:
        date_str: Date string from API (format: YYYYMMDD or ISO format)
        
    Returns:
        Formatted date string (YYYY-MM-DD) or current date
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Try YYYYMMDD format (common in GDELT)
        if len(date_str) == 8 and date_str.isdigit():
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return datetime(year, month, day).strftime("%Y-%m-%d")
        
        # Try ISO format
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
            try:
                dt = datetime.strptime(date_str[:10], fmt)
                return dt.strftime("%Y-%m-%d")
            except:
                continue
        
        return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

def get_gdelt_events_multiple_diseases(diseases: List[str] = None) -> pd.DataFrame:
    """
    Fetch GDELT events for multiple diseases
    
    Args:
        diseases: List of disease names
        
    Returns:
        Combined DataFrame with all events
    """
    if diseases is None:
        diseases = ["dengue", "malaria", "cholera", "influenza", "covid", "monkeypox", "hepatitis", "typhoid", "tuberculosis", "meningitis"]
    
    all_events = []
    
    for disease in diseases:
        query = f"{disease} Pakistan"
        df = get_gdelt_health_events(query)
        if not df.empty:
            all_events.append(df)
    
    if all_events:
        return pd.concat(all_events, ignore_index=True)
    else:
        return pd.DataFrame(columns=["title", "seendate", "domain", "url"])


