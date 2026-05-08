"""
Working API Fetcher - Uses verified working API endpoints
Updated with proper URL encoding and headers
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from src.working_disease_apis import DISEASE_SOURCES
from pathlib import Path
import io

# ============================
# UNIVERSAL REQUEST FUNCTION
# ============================
def safe_get(url: str) -> Optional[dict]:
    """
    Safe GET request with proper headers and error handling
    
    Args:
        url: API URL
    
    Returns:
        JSON response as dict, or None if failed
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # If server blocks direct request â†’ 404 or 403
        if response.status_code in [403, 404]:
            return None
        
        return response.json()
    except:
        return None

def fetch_who_disease_data(url: str, disease_name: str) -> pd.DataFrame:
    """
    Fetch disease data from WHO GHO API
    
    Args:
        url: WHO API URL
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        # Use safe_get with proper headers
        data_dict = safe_get(url)
        
        if data_dict is None:
            print(f"  âš  {disease_name}: API unavailable or returned 404/empty")
            return pd.DataFrame()
        
        data = data_dict.get("value", [])
        
        for record in data:
            year = record.get("TimeDim")
            if year and 2015 <= year <= 2025:
                # Try multiple value fields
                value = (record.get("NumericValue") or 
                        record.get("Value") or 
                        record.get("Numeric") or
                        record.get("Count") or 0)
                
                try:
                    if isinstance(value, str):
                        value = value.split("[")[0].strip()
                        value = value.replace(" ", "").replace(",", "")
                        value = float(value)
                    else:
                        value = float(value) if value else 0
                    
                    if value and value > 0:
                        all_records.append({
                            "year": int(year),
                            "district": "Pakistan",  # Country-level, will be distributed
                            "disease": disease_name,
                            "cases": int(value),
                            "source": "WHO GHO API",
                            "type": "historical_verified"
                        })
                except (ValueError, TypeError):
                    continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from WHO API")
        
    except Exception as e:
        print(f"  âš  {disease_name}: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_disease_sh_data(url: str, disease_name: str) -> pd.DataFrame:
    """
    Fetch disease data from Disease.sh API (COVID-19)
    
    Args:
        url: Disease.sh API URL
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"  âš  {disease_name}: Disease.sh API returned {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        
        # Disease.sh returns historical data with dates
        if 'timeline' in data and 'cases' in data['timeline']:
            cases_data = data['timeline']['cases']
            for date_str, cases in cases_data.items():
                try:
                    date = pd.to_datetime(date_str)
                    year = date.year
                    if 2015 <= year <= 2025:
                        all_records.append({
                            "year": year,
                            "district": "Pakistan",  # Country-level
                            "disease": disease_name,
                            "cases": int(cases) if cases else 0,
                            "source": "Disease.sh API",
                            "type": "real_time"
                        })
                except:
                    continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from Disease.sh API")
        
    except Exception as e:
        print(f"  âš  {disease_name}: Disease.sh API failed: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_epidemicforecasting_data(url: str, disease_name: str) -> pd.DataFrame:
    """
    Fetch disease data from Epidemic Forecasting API (Dengue)
    
    Args:
        url: Epidemic Forecasting API URL
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"  âš  {disease_name}: Epidemic Forecasting API returned {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        
        # Process response based on structure
        if isinstance(data, list):
            for item in data:
                try:
                    date_str = item.get('date', item.get('Date', ''))
                    if date_str:
                        date = pd.to_datetime(date_str)
                        year = date.year
                    else:
                        year = datetime.now().year
                    
                    cases = item.get('cases', item.get('count', 0))
                    district = item.get('district', item.get('location', 'Pakistan'))
                    
                    if 2015 <= year <= 2025:
                        all_records.append({
                            "year": year,
                            "district": district,
                            "disease": disease_name,
                            "cases": int(cases) if cases else 0,
                            "source": "Epidemic Forecasting API",
                            "type": "real_time"
                        })
                except:
                    continue
        elif isinstance(data, dict):
            # Handle dict response
            for key, value in data.items():
                try:
                    if isinstance(value, (int, float)):
                        year = datetime.now().year
                        all_records.append({
                            "year": year,
                            "district": "Pakistan",
                            "disease": disease_name,
                            "cases": int(value),
                            "source": "Epidemic Forecasting API",
                            "type": "real_time"
                        })
                except:
                    continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from Epidemic Forecasting API")
        
    except Exception as e:
        print(f"  âš  {disease_name}: Epidemic Forecasting API failed: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_healthmap_disease_data(url: str, disease_name: str) -> pd.DataFrame:
    """
    Fetch disease data from HealthMap API
    
    Args:
        url: HealthMap API URL
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        # Use proper headers
        headers = {
            "Accept": "application/json"
        }
        
        # Try direct request with headers
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                except:
                    data = response.text
            else:
                print(f"  âš  {disease_name}: HealthMap API returned {response.status_code}")
                return pd.DataFrame()
        except:
            # Fallback to safe_get
            data = safe_get(url)
            if data is None:
                print(f"  âš  {disease_name}: HealthMap API unavailable or returned 404/empty")
                return pd.DataFrame()
        
        # Handle different response formats
        if isinstance(data, dict):
            alerts = data.get("alerts", data.get("data", data.get("cases", [])))
        elif isinstance(data, list):
            alerts = data
        else:
            alerts = []
        
        # Process alerts
        for alert in alerts:
            if isinstance(alert, dict):
                try:
                    # Extract date
                    date_str = alert.get("date", alert.get("Date", alert.get("published", "")))
                    if date_str:
                        date = pd.to_datetime(date_str)
                        year = date.year
                    else:
                        year = datetime.now().year
                    
                    # Extract district
                    district = "Pakistan"
                    location = alert.get("location", alert.get("city", alert.get("Location", "")))
                    
                    pakistan_districts = [
                        "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
                        "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala",
                        "Hyderabad", "Sargodha", "Bahawalpur", "Sukkur", "Larkana"
                    ]
                    
                    for dist in pakistan_districts:
                        if dist.lower() in str(location).lower():
                            district = dist
                            break
                    
                    # Extract cases
                    cases = alert.get("cases", alert.get("count", 1))
                    if not isinstance(cases, (int, float)):
                        cases = 1
                    
                    if 2015 <= year <= 2025:
                        all_records.append({
                            "year": year,
                            "district": district,
                            "disease": disease_name,
                            "cases": int(cases),
                            "source": "HealthMap API",
                            "type": "real_time"
                        })
                except Exception as e:
                    continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from HealthMap API")
        
    except Exception as e:
        print(f"  âš  {disease_name}: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_local_csv_disease_data(csv_path: str, disease_name: str) -> pd.DataFrame:
    """
    Load disease data from local CSV file
    
    Args:
        csv_path: Path to local CSV file
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        from pathlib import Path
        csv_file = Path(csv_path)
        
        if not csv_file.exists():
            print(f"  âš  {disease_name}: CSV file not found: {csv_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_file)
        
        if df.empty:
            print(f"  âš  {disease_name}: Empty CSV file")
            return pd.DataFrame()
        
        # Process CSV data - expected columns: disease, date, district, lat, lon, cases
        for _, row in df.iterrows():
            try:
                # Extract date and year
                date_str = row.get('date', '')
                if date_str:
                    date = pd.to_datetime(date_str)
                    year = date.year
                else:
                    year = datetime.now().year
                
                # Extract district
                district = row.get('district', 'Pakistan')
                
                # Extract cases
                cases = row.get('cases', 0)
                if pd.isna(cases):
                    cases = 0
                
                # Accept all years from CSV (2010-2025 for comprehensive data)
                if 2010 <= year <= 2025:
                    all_records.append({
                        "year": int(year),
                        "district": district,
                        "disease": disease_name,
                        "cases": int(cases),
                        "source": f"Local CSV ({csv_file.name})",
                        "type": "historical_verified"
                    })
            except Exception as e:
                continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from local CSV")
        
    except Exception as e:
        print(f"  âš  {disease_name}: Local CSV load failed: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_csv_disease_data(url: str, disease_name: str) -> pd.DataFrame:
    """
    Fetch disease data from CSV URL (WHO GHO CSV endpoints or GitHub)
    
    Args:
        url: CSV URL
        disease_name: Name of the disease
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    all_records = []
    
    try:
        headers = {
            "Accept": "text/csv,application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"  âš  {disease_name}: CSV URL returned {response.status_code}")
            return pd.DataFrame()
        
        # Try to parse as CSV
        try:
            df = pd.read_csv(io.StringIO(response.text))
        except:
            # Try JSON if CSV fails (some WHO endpoints return JSON)
            try:
                data = response.json()
                if isinstance(data, dict) and "value" in data:
                    df = pd.DataFrame(data["value"])
                else:
                    df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()
            except:
                print(f"  âš  {disease_name}: Could not parse CSV/JSON response")
                return pd.DataFrame()
        
        if df.empty:
            print(f"  âš  {disease_name}: Empty CSV/JSON response")
            return pd.DataFrame()
        
        # Process CSV data - look for Pakistan data
        pakistan_df = df[df.get('SpatialDim', df.get('Country', '')).astype(str).str.contains('PAK|Pakistan', case=False, na=False)]
        
        if pakistan_df.empty and len(df) > 0:
            # If no Pakistan filter column, use all data
            pakistan_df = df
        
        # Extract year and value columns
        for _, row in pakistan_df.iterrows():
            try:
                # Try to find year column
                year = None
                for year_col in ['TimeDim', 'Year', 'year', 'Date', 'date']:
                    if year_col in row and pd.notna(row[year_col]):
                        try:
                            if isinstance(row[year_col], (int, float)):
                                year = int(row[year_col])
                            else:
                                date = pd.to_datetime(row[year_col])
                                year = date.year
                            break
                        except:
                            continue
                
                if not year or not (2015 <= year <= 2025):
                    continue
                
                # Try to find value column
                value = None
                for value_col in ['NumericValue', 'Value', 'Numeric', 'Count', 'cases', 'Cases']:
                    if value_col in row and pd.notna(row[value_col]):
                        try:
                            val = row[value_col]
                            if isinstance(val, str):
                                val = val.split("[")[0].strip()
                                val = val.replace(" ", "").replace(",", "")
                            value = float(val) if val else 0
                            break
                        except:
                            continue
                
                if value and value > 0:
                    all_records.append({
                        "year": int(year),
                        "district": "Pakistan",  # Country-level, will be distributed
                        "disease": disease_name,
                        "cases": int(value),
                        "source": f"CSV ({url.split('/')[-1]})",
                        "type": "historical_verified"
                    })
            except Exception as e:
                continue
        
        print(f"  âœ“ {disease_name}: {len(all_records)} records from CSV")
        
    except Exception as e:
        print(f"  âš  {disease_name}: CSV fetch failed: {str(e)}")
    
    return pd.DataFrame(all_records)

def fetch_all_working_apis(start_year: int = 2010, end_year: int = 2025) -> pd.DataFrame:
    """
    Fetch data from all working disease APIs and CSV sources
    Prioritizes CSV files (comprehensive 2010-2025 data) over APIs
    
    Args:
        start_year: Start year (default: 2010 to match CSV data)
        end_year: End year (default: 2025)
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    print("=" * 60)
    print("Fetching Data from Working Disease APIs")
    print("=" * 60)
    print()
    
    all_dataframes = []
    
    for disease_name, source_config in DISEASE_SOURCES.items():
        source_type = source_config.get("type")
        url = source_config.get("url")
        use_api = source_config.get("use_api", False)
        
        # Check for local CSV first (for monkeypox)
        if disease_name == "monkeypox":
            from src.monkeypox_api import load_monkeypox_from_local_csv
            local_df = load_monkeypox_from_local_csv()
            if not local_df.empty:
                all_dataframes.append(local_df)
                continue
        
        # Prioritize CSV files (comprehensive historical data)
        if source_type == "csv":
            csv_path = source_config.get("path", "")
            if csv_path and Path(csv_path).exists():
                # Local CSV file (preferred - comprehensive data)
                df = fetch_local_csv_disease_data(csv_path, disease_name)
                if not df.empty:
                    all_dataframes.append(df)
                    continue
            elif csv_path and csv_path.startswith("http"):
                # Remote CSV URL
                df = fetch_csv_disease_data(csv_path, disease_name)
                if not df.empty:
                    all_dataframes.append(df)
                    continue
        
        # Try API only if use_api is True and CSV failed/not available
        if source_type == "api" and use_api:
            url = source_config.get("url", "")
            # Determine API type by URL
            if "disease.sh" in url:
                df = fetch_disease_sh_data(url, disease_name)
            elif "epidemicforecasting.org" in url:
                df = fetch_epidemicforecasting_data(url, disease_name)
            elif "ghoapi.azureedge.net" in url:
                df = fetch_who_disease_data(url, disease_name)
            elif "healthmap.org" in url:
                df = fetch_healthmap_disease_data(url, disease_name)
            elif "who.int" in url:
                # WHO GHO API with indicator
                indicator = source_config.get("indicator", "")
                if indicator:
                    # Use WHO API fetcher with indicator
                    who_url = f"https://ghoapi.azureedge.net/api/{indicator}?$filter=SpatialDim%20eq%20%27PAK%27"
                    df = fetch_who_disease_data(who_url, disease_name)
                else:
                    print(f"  âš  {disease_name}: WHO API requires indicator")
                    df = pd.DataFrame()
            else:
                print(f"  âš  {disease_name}: Unknown API type for URL: {url}")
                df = pd.DataFrame()
        else:
            # No valid source type or CSV already handled above
            df = pd.DataFrame()
        
        if not df.empty:
            # Filter by year range
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
            if not df.empty:
                all_dataframes.append(df)
    
    # Combine all dataframes
    if all_dataframes:
        unified_df = pd.concat(all_dataframes, ignore_index=True)
        
        print()
        print("=" * 60)
        print(f"âœ“ Working APIs Data: {len(unified_df):,} total records")
        print(f"  Years: {unified_df['year'].min()} to {unified_df['year'].max()}")
        print(f"  Diseases: {sorted(unified_df['disease'].unique())}")
        print("=" * 60)
        
        return unified_df
    else:
        print("\nâš  No data loaded from working APIs")
        return pd.DataFrame(columns=["year", "district", "disease", "cases", "source", "type"])

