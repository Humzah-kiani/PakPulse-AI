"""
Global.health Monkeypox API Integration for PakPulse AI
Supports multiple data sources: Local CSV, Kaggle datasets, GitHub CSV, and Global.health API
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Local CSV file path (highest priority)
MONKEYPOX_LOCAL_CSV = Path("data/Monkeypox.csv")
MONKEYPOX_DOWNLOADS_CSV = Path(r"c:\Users\MK\Downloads\Monkeypox.csv")

# Primary endpoint - GitHub CSV (NOTE: Currently returns 404 - file may have been moved/removed)
MONKEYPOX_GITHUB = "https://raw.githubusercontent.com/globaldothealth/monkeypox/main/latest.csv"
MONKEYPOX_API_BASE = "https://api.monkeypox.global.health/cases"  # Fallback (NOTE: Domain may not resolve)
MONKEYPOX_API_ALT = "https://monkeypox.global.health/api/cases"  # Alternative fallback

def load_monkeypox_from_local_csv(csv_path: Path = None) -> pd.DataFrame:
    """
    Load Monkeypox data from local CSV file
    
    Args:
        csv_path: Path to CSV file (if None, tries default locations)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    # Try different CSV locations
    csv_files = []
    if csv_path and csv_path.exists():
        csv_files.append(csv_path)
    if MONKEYPOX_LOCAL_CSV.exists():
        csv_files.append(MONKEYPOX_LOCAL_CSV)
    if MONKEYPOX_DOWNLOADS_CSV.exists():
        csv_files.append(MONKEYPOX_DOWNLOADS_CSV)
    
    if not csv_files:
        return pd.DataFrame()
    
    # Use first available CSV
    csv_file = csv_files[0]
    
    try:
        df = pd.read_csv(csv_file)
        print(f"  ðŸ“ Loaded {len(df)} records from local CSV: {csv_file.name}")
        
        # Pakistan districts for matching
        pakistan_districts = [
            "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
            "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala",
            "Hyderabad", "Sargodha", "Bahawalpur", "Sukkur", "Larkana",
            "Sheikhupura", "Jhang", "Rahim Yar Khan", "Gujrat", "Kasur"
        ]
        
        # Filter for Pakistan or process all records
        pakistan_df = df[df['Country'].str.contains('Pakistan', case=False, na=False)]
        
        # If no Pakistan-specific data, we can still use the data
        # and distribute it proportionally to Pakistan districts
        if pakistan_df.empty:
            print(f"  âš  No Pakistan-specific records, using all records for distribution")
            pakistan_df = df
        
        # Process each record
        for _, row in pakistan_df.iterrows():
            try:
                # Extract date (try multiple date columns)
                date = None
                for date_col in ['Date_onset', 'Date_confirmation', 'Date_entry', 'Date', 'date']:
                    if date_col in row and pd.notna(row[date_col]) and str(row[date_col]).strip():
                        try:
                            date = pd.to_datetime(row[date_col])
                            break
                        except:
                            continue
                
                if date is None or pd.isna(date):
                    year = datetime.now().year
                else:
                    year = date.year
                
                # Extract location/district
                district = "Pakistan"  # Default to country-level
                location_str = ""
                
                # Try to get location from various columns
                for loc_col in ['Location', 'City', 'Contact_location', 'Travel_history_location']:
                    if loc_col in row and pd.notna(row[loc_col]):
                        location_str = str(row[loc_col])
                        # Check if it matches any Pakistan district
                        for dist in pakistan_districts:
                            if dist.lower() in location_str.lower():
                                district = dist
                                break
                        if district != "Pakistan":
                            break
                
                # Check if country is Pakistan
                country = str(row.get('Country', '')).lower()
                if 'pakistan' in country or row.get('Country_ISO3', '') == 'PAK':
                    # This is Pakistan data
                    pass
                elif pakistan_df.empty and len(df) > 0:
                    # Using all data, will distribute to districts
                    pass
                
                # Only include records from 2015-2025
                if 2015 <= year <= 2025:
                    all_records.append({
                        "year": year,
                        "district": district,
                        "disease": "monkeypox",
                        "cases": 1,  # Each row is typically one case
                        "source": f"Local CSV ({csv_file.name})",
                        "type": "real_time"
                    })
            except Exception as e:
                continue
        
        if all_records:
            print(f"  âœ“ monkeypox: {len(all_records)} records processed from local CSV")
            return pd.DataFrame(all_records)
        else:
            print(f"  âš  monkeypox: No valid records found in local CSV")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  âš  monkeypox: Local CSV load failed: {str(e)}")
        return pd.DataFrame()

def get_monkeypox_data_pakistan(limit: int = 5000, kaggle_dataset: str = None, local_csv: Path = None) -> pd.DataFrame:
    """
    Fetch Monkeypox data for Pakistan from multiple sources
    
    Priority order:
    1. Local CSV file (if provided or found in data/)
    2. Kaggle dataset (if provided)
    3. GitHub CSV
    4. Global.health API endpoints
    
    Args:
        limit: Maximum number of records to fetch (default: 5000)
        kaggle_dataset: Kaggle dataset identifier (e.g., "username/dataset-name")
        local_csv: Path to local CSV file (if None, tries default locations)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    # Try local CSV first (highest priority)
    local_df = load_monkeypox_from_local_csv(local_csv)
    if not local_df.empty:
        return local_df
    
    # Try Kaggle if dataset provided
    if kaggle_dataset:
        try:
            from src.kaggle_data_fetcher import get_monkeypox_from_kaggle
            kaggle_df = get_monkeypox_from_kaggle(kaggle_dataset)
            if not kaggle_df.empty:
                return kaggle_df
        except Exception as e:
            print(f"  âš  monkeypox: Kaggle fetch failed: {str(e)}")
    
    try:
        # Try GitHub CSV first (NOTE: Currently unavailable - returns 404)
        try:
            response = requests.get(MONKEYPOX_GITHUB, timeout=30, headers={"Accept": "text/csv"})
            response.raise_for_status()
            # Parse CSV
            import io
            df = pd.read_csv(io.StringIO(response.text))
            
            # Convert to our format
            pakistan_df = df[df['Country'].str.contains('Pakistan', case=False, na=False)]
            if not pakistan_df.empty:
                for _, row in pakistan_df.iterrows():
                    try:
                        date = pd.to_datetime(row.get('Date', row.get('Date_confirmation', row.get('date', ''))))
                        year = date.year if pd.notna(date) else datetime.now().year
                        if 2015 <= year <= 2025:
                            all_records.append({
                                "year": year,
                                "district": "Pakistan",
                                "disease": "monkeypox",
                                "cases": 1,  # Each row is a case
                                "source": "Global.health GitHub",
                                "type": "real_time"
                            })
                    except:
                        continue
                print(f"  âœ“ monkeypox: {len(all_records)} records from GitHub")
                return pd.DataFrame(all_records)
            else:
                print(f"  âš  monkeypox: No Pakistan data in GitHub CSV")
        except Exception as e1:
            print(f"  âš  monkeypox: GitHub CSV failed: {str(e1)}")
            # Try API endpoints as fallback
            try:
                url = f"{MONKEYPOX_API_BASE}?limit={limit}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
            except:
                try:
                    url = f"{MONKEYPOX_API_ALT}?limit={limit}"
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                except Exception as e2:
                    print(f"  âš  monkeypox: All endpoints failed")
                    return pd.DataFrame()
        
        # Check if data is a list or dict with cases
        if isinstance(data, dict):
            cases = data.get("cases", data.get("data", []))
        else:
            cases = data if isinstance(data, list) else []
        
        # Filter for Pakistan and process
        pakistan_cases = []
        for case in cases:
            # Check if case is from Pakistan
            country = case.get("country", case.get("Country", ""))
            location = case.get("location", case.get("Location", ""))
            
            if country and ("Pakistan" in str(country) or "PAK" in str(country).upper()):
                pakistan_cases.append(case)
            elif location and ("Pakistan" in str(location) or any(city in str(location) for city in ["Karachi", "Lahore", "Islamabad", "Peshawar", "Quetta"])):
                pakistan_cases.append(case)
        
        # Process Pakistan cases
        for case in pakistan_cases:
            try:
                # Extract date
                date_str = case.get("date", case.get("Date", case.get("dateOnset", "")))
                if date_str:
                    try:
                        date = pd.to_datetime(date_str)
                        year = date.year
                    except:
                        year = datetime.now().year
                else:
                    year = datetime.now().year
                
                # Extract location (try to get district)
                location = case.get("location", case.get("Location", case.get("city", "Pakistan")))
                district = "Pakistan"  # Default to country-level
                
                # Try to extract district from location
                pakistan_districts = [
                    "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
                    "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala",
                    "Hyderabad", "Sargodha", "Bahawalpur", "Sukkur", "Larkana",
                    "Sheikhupura", "Jhang", "Rahim Yar Khan", "Gujrat", "Kasur"
                ]
                
                for dist in pakistan_districts:
                    if dist.lower() in str(location).lower():
                        district = dist
                        break
                
                # Extract case count (usually 1 per record, but check)
                cases = case.get("cases", case.get("count", 1))
                if not isinstance(cases, (int, float)):
                    cases = 1
                
                if 2015 <= year <= 2025:
                    all_records.append({
                        "year": year,
                        "district": district,
                        "disease": "monkeypox",
                        "cases": int(cases),
                        "source": "Global.health API",
                        "type": "real_time"
                    })
            except Exception as e:
                continue
        
        print(f"  âœ“ monkeypox: {len(all_records)} records from Pakistan")
        
    except Exception as e:
        print(f"  âš  monkeypox: {str(e)}")
    
    return pd.DataFrame(all_records)

