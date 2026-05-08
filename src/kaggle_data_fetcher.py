"""
Kaggle Dataset Fetcher for PakPulse AI
Fetches CSV files from Kaggle datasets
"""

import os
import pandas as pd
from typing import Optional, List
from pathlib import Path

def setup_kaggle_credentials(username: str = None, api_key: str = None):
    """
    Setup Kaggle API credentials
    
    Args:
        username: Kaggle username (or set KAGGLE_USERNAME env var)
        api_key: Kaggle API key (or set KAGGLE_KEY env var)
    
    Returns:
        True if credentials are set, False otherwise
    """
    # Check if credentials already exist BEFORE importing kaggle
    # (kaggle package tries to authenticate on import)
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if kaggle_json.exists():
        try:
            import kaggle  # Only import if credentials exist
            print("  [OK] Kaggle credentials found")
            return True
        except Exception as e:
            print(f"  [!] Kaggle import failed: {str(e)}")
            return False
    
    # Try to use provided credentials
    if username and api_key:
        kaggle_dir.mkdir(exist_ok=True)
        kaggle_json.write_text(f'{{"username":"{username}","key":"{api_key}"}}')
        os.chmod(kaggle_json, 0o600)  # Set permissions
        print("  [OK] Kaggle credentials saved")
        return True
    
    # Try environment variables
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        kaggle_dir.mkdir(exist_ok=True)
        kaggle_json.write_text(
            f'{{"username":"{os.getenv("KAGGLE_USERNAME")}","key":"{os.getenv("KAGGLE_KEY")}"}}'
        )
        os.chmod(kaggle_json, 0o600)
        print("  [OK] Kaggle credentials set from environment")
        return True
    
    print("  [!] Kaggle credentials not found. Please:")
    print("     1. Get your API key from: https://www.kaggle.com/settings")
    print("     2. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables, OR")
    print("     3. Place kaggle.json in ~/.kaggle/ with format:")
    print('        {"username":"your_username","key":"your_api_key"}')
    return False


def fetch_kaggle_dataset(dataset: str, file_name: str = None, unzip: bool = True) -> Optional[pd.DataFrame]:
    """
    Fetch a CSV file from a Kaggle dataset
    
    Args:
        dataset: Dataset identifier in format "username/dataset-name"
        file_name: Specific CSV file to download (if None, downloads all and returns first CSV)
        unzip: Whether to unzip downloaded files
    
    Returns:
        DataFrame with the CSV data, or None if failed
    """
    try:
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
        except ImportError:
            print("  [!] Kaggle package not installed. Run: pip install kaggle")
            return None
        
        # Setup credentials
        if not setup_kaggle_credentials():
            return None
        
        # Initialize API
        api = KaggleApi()
        api.authenticate()
        
        # Download dataset
        print(f"  [ðŸ“¥] Downloading Kaggle dataset: {dataset}")
        api.dataset_download_files(dataset, path="data/kaggle_temp", unzip=unzip)
        
        # Find CSV file(s)
        temp_dir = Path("data/kaggle_temp")
        csv_files = list(temp_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"  [!] No CSV files found in dataset: {dataset}")
            return None
        
        # Load specified file or first CSV
        if file_name:
            csv_path = temp_dir / file_name
            if not csv_path.exists():
                print(f"  [!] File not found: {file_name}")
                return None
        else:
            csv_path = csv_files[0]
        
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"  [OK] Loaded {len(df)} records from {csv_path.name}")
        
        return df
        
    except Exception as e:
        print(f"  [!] Kaggle dataset fetch failed: {str(e)}")
        return None


def get_monkeypox_from_kaggle(dataset: str = None) -> pd.DataFrame:
    """
    Fetch Monkeypox data from Kaggle
    
    Args:
        dataset: Dataset identifier (e.g., "username/monkeypox-dataset")
                 If None, will try common monkeypox dataset names
    
    Returns:
        DataFrame with columns: [year, district, disease, cases, source, type]
    """
    from datetime import datetime
    
    # Common monkeypox dataset identifiers to try
    common_datasets = [
        dataset,  # User-provided dataset
        "zainabelsayedtaha/monkeypox-skin-lesion",  # From the notebook URL
        "deepcontractor/monkeypox-dataset",
        "monkeypox-cases",
    ]
    
    all_records = []
    
    for dataset_id in common_datasets:
        if not dataset_id:
            continue
            
        try:
            df = fetch_kaggle_dataset(dataset_id)
            
            if df is None or df.empty:
                continue
            
            # Try to find relevant columns
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            country_cols = [col for col in df.columns if 'country' in col.lower() or 'location' in col.lower()]
            case_cols = [col for col in df.columns if 'case' in col.lower() or 'count' in col.lower()]
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Extract date
                    date = None
                    for col in date_cols:
                        try:
                            date = pd.to_datetime(row[col])
                            break
                        except:
                            continue
                    
                    if date is None or pd.isna(date):
                        year = datetime.now().year
                    else:
                        year = date.year
                    
                    # Check if Pakistan-related
                    is_pakistan = False
                    for col in country_cols:
                        if pd.notna(row[col]) and "pakistan" in str(row[col]).lower():
                            is_pakistan = True
                            break
                    
                    # If no country column, assume it's global data
                    if not country_cols:
                        is_pakistan = True  # Include all if no country filter
                    
                    if is_pakistan and 2015 <= year <= 2025:
                        # Extract case count
                        cases = 1
                        for col in case_cols:
                            try:
                                val = row[col]
                                if pd.notna(val):
                                    cases = int(float(val))
                                    break
                            except:
                                continue
                        
                        all_records.append({
                            "year": year,
                            "district": "Pakistan",  # Default to country-level
                            "disease": "monkeypox",
                            "cases": cases,
                            "source": f"Kaggle ({dataset_id})",
                            "type": "real_time"
                        })
                except Exception as e:
                    continue
            
            if all_records:
                print(f"  [OK] monkeypox: {len(all_records)} records from Kaggle")
                return pd.DataFrame(all_records)
                
        except Exception as e:
            print(f"  [!] Kaggle dataset {dataset_id} failed: {str(e)}")
            continue
    
    if not all_records:
        print(f"  [!] monkeypox: No data found in Kaggle datasets")
    
    return pd.DataFrame(all_records)

