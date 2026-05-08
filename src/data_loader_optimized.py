#!/usr/bin/env python3
"""
Optimized data loading module for PakPulse AI GIS Dashboard
Fixes performance issues and ensures all 50 districts and 20 diseases are loaded
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

# Base data directory
DATA_DIR = Path(__file__).parent.parent / "data"

def vectorized_calculate_risk_index(disease_series: pd.Series, cases_per_100k_series: pd.Series) -> np.ndarray:
    """
    Vectorized calculation of risk index for all rows at once
    Much faster than row-by-row iteration
    
    Args:
        disease_series: Series with disease names
        cases_per_100k_series: Series with cases per 100k
        
    Returns:
        Array of risk indices
    """
    # Thresholds for different diseases
    thresholds_map = {
        "dengue": (10, 50, 100, 200),
        "malaria": (20, 100, 200, 500),
        "cholera": (5, 20, 50, 100),
        "covid-19": (50, 200, 500, 1000),
        "covid19": (50, 200, 500, 1000),
        "influenza": (100, 500, 1000, 2000),
        "diarrhea": (20, 50, 100, 200),
        "hepatitis a": (5, 15, 30, 60),
        "hepatitis e": (5, 15, 30, 60),
        "eye infection": (50, 100, 200, 500),
        "food poisoning": (10, 50, 100, 200),
        "heatstroke": (50, 100, 200, 500),
        "measles": (5, 20, 50, 100),
        "mumps": (5, 20, 50, 100),
        "pneumonia": (20, 100, 200, 500),
        "polio": (1, 5, 10, 20),
        "rotavirus": (20, 50, 100, 200),
        "skin infection": (50, 100, 200, 500),
        "tuberculosis": (5, 20, 50, 100),
        "typhoid": (5, 20, 50, 100),
        "whooping cough": (5, 20, 50, 100),
    }
    
    # Normalize disease names
    disease_lower = disease_series.str.lower()
    
    risk_indices = np.zeros(len(disease_series))
    
    for disease_key, (low, moderate, high, very_high) in thresholds_map.items():
        # Find all rows with this disease
        mask = disease_lower == disease_key
        
        if mask.sum() == 0:
            continue
        
        cases = cases_per_100k_series[mask]
        
        # Vectorized calculation of risk indices for this disease
        risk = np.zeros_like(cases, dtype=float)
        
        # Low risk: 0-20
        low_mask = cases < low
        risk[low_mask] = np.minimum(20, (cases[low_mask] / low) * 20)
        
        # Moderate risk: 20-40
        moderate_mask = (cases >= low) & (cases < moderate)
        risk[moderate_mask] = 20 + ((cases[moderate_mask] - low) / (moderate - low)) * 20
        
        # High risk: 40-60
        high_mask = (cases >= moderate) & (cases < high)
        risk[high_mask] = 40 + ((cases[high_mask] - moderate) / (high - moderate)) * 20
        
        # Very high risk: 60-80
        very_high_mask = (cases >= high) & (cases < very_high)
        risk[very_high_mask] = 60 + ((cases[very_high_mask] - high) / (very_high - high)) * 20
        
        # Critical risk: 80-100
        critical_mask = cases >= very_high
        risk[critical_mask] = np.minimum(100, 80 + ((cases[critical_mask] - very_high) / very_high) * 20)
        
        # Assign to result array
        risk_indices[mask] = risk
    
    # For any unmapped diseases, use dengue thresholds
    unmapped = ~disease_lower.isin(thresholds_map.keys())
    if unmapped.sum() > 0:
        cases = cases_per_100k_series[unmapped].values
        low, moderate, high, very_high = thresholds_map["dengue"]
        
        risk = np.zeros_like(cases, dtype=float)
        low_mask = cases < low
        risk[low_mask] = np.minimum(20, (cases[low_mask] / low) * 20)
        moderate_mask = (cases >= low) & (cases < moderate)
        risk[moderate_mask] = 20 + ((cases[moderate_mask] - low) / (moderate - low)) * 20
        high_mask = (cases >= moderate) & (cases < high)
        risk[high_mask] = 40 + ((cases[high_mask] - moderate) / (high - moderate)) * 20
        very_high_mask = (cases >= high) & (cases < very_high)
        risk[very_high_mask] = 60 + ((cases[very_high_mask] - high) / (very_high - high)) * 20
        critical_mask = cases >= very_high
        risk[critical_mask] = np.minimum(100, 80 + ((cases[critical_mask] - very_high) / very_high) * 20)
        
        risk_indices[unmapped] = risk
    
    return risk_indices


def load_pakpulse_csv_optimized(csv_path: str = None) -> pd.DataFrame:
    """
    Load the pakpulse_250k_realistic.csv dataset with optimizations
    - Vectorized operations instead of iterrows
    - Proper handling of all 20 diseases
    - Comprehensive error checking
    
    Args:
        csv_path: Path to the CSV file. If None, looks for it in Desktop or data directory
    
    Returns:
        DataFrame in standard PakPulse format with columns:
        [district, latitude, longitude, disease, risk_index, date, cases_reported, population]
    """
    
    # Try to find the CSV file
    if csv_path is None:
        desktop_path = Path.home() / "Desktop" / "pakpulse_250k_realistic.csv"
        if desktop_path.exists():
            csv_path = str(desktop_path)
        else:
            data_path = DATA_DIR / "pakpulse_250k_realistic.csv"
            if data_path.exists():
                csv_path = str(data_path)
            else:
                raise FileNotFoundError(
                    "pakpulse_250k_realistic.csv not found. "
                    "Please provide the path or place it in Desktop or data/ directory."
                )
    
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"\nðŸ“Š Loading dataset from: {csv_path}")
    
    # Load CSV with appropriate dtypes for efficiency
    dtypes = {
        'date': 'object',
        'district': 'object',
        'lat': 'float32',
        'lon': 'float32',
        'disease': 'object',
        'cases': 'float32',
        'temperature': 'float32',
        'humidity': 'float32',
        'rainfall': 'float32',
        'population_density': 'float32',
        'sanitation_index': 'float32',
    }
    
    try:
        df = pd.read_csv(csv_path, low_memory=False, dtype=dtypes)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        # Fallback without dtypes
        df = pd.read_csv(csv_path, low_memory=False)
    
    print(f"âœ“ Loaded {len(df):,} records")
    print(f"  Columns: {list(df.columns)}")
    
    # Ensure all required columns exist
    required_columns = ['district', 'lat', 'lon', 'disease', 'cases', 'temperature', 'humidity', 'rainfall', 'sanitation_index', 'population_density']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"âš  Warning: Missing columns: {missing}")
    
    # Convert date to datetime
    print("  Converting date...")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    print("  Standardizing column names...")
    # Standardize column names
    df = df.rename(columns={
        'lat': 'latitude',
        'lon': 'longitude',
        'cases': 'cases_reported'
    })
    
    print("  Calculating risk indices (vectorized)...")
    # Calculate cases per 100k VECTORIZED
    # estimated_population = population_density * 5000
    estimated_population = df['population_density'] * 5000
    df['cases_per_100k'] = (df['cases_reported'] / estimated_population) * 100000
    df['cases_per_100k'] = df['cases_per_100k'].fillna(0).clip(0, 100000)
    
    # Apply vectorized risk calculation
    df['risk_index'] = vectorized_calculate_risk_index(df['disease'], df['cases_per_100k'])
    
    # Apply environmental adjustments
    print("  Applying environmental adjustments...")
    disease_lower = df['disease'].str.lower()
    
    # Temperature/humidity bonus for mosquito diseases
    mosquito_diseases = disease_lower.isin(['dengue', 'malaria'])
    temp_humidity_bonus = np.zeros(len(df))
    temp_humidity_bonus[mosquito_diseases & (df['temperature'] > 25) & (df['humidity'] > 60)] = 0.1
    temp_humidity_bonus[mosquito_diseases & (df['rainfall'] > 50)] += 0.05
    
    # Poor sanitation bonus
    sanitation_bonus = np.zeros(len(df))
    sanitation_bonus[df['sanitation_index'] < 50] = 0.1
    
    # Add environmental adjustments
    df['risk_index'] = df['risk_index'] * (1 + temp_humidity_bonus + sanitation_bonus)
    df['risk_index'] = df['risk_index'].clip(0, 100)  # Ensure 0-100 range
    
    # Calculate population
    df['population'] = (df['population_density'] * 5000).astype(int)
    
    # Build final dataframe with only required columns
    print("  Selecting final columns...")
    result_columns = ['district', 'latitude', 'longitude', 'disease', 'risk_index', 'date', 'cases_reported', 'population']
    result_df = df[result_columns].copy()
    
    # Remove any rows with missing essential data
    initial_len = len(result_df)
    result_df = result_df.dropna(subset=['district', 'disease', 'date', 'latitude', 'longitude'])
    dropped = initial_len - len(result_df)
    
    if dropped > 0:
        print(f"  Dropped {dropped} rows with missing data")
    
    print(f"\nâœ… DATA LOADING COMPLETE")
    print(f"   Total records: {len(result_df):,}")
    print(f"   Date range: {result_df['date'].min().date()} to {result_df['date'].max().date()}")
    print(f"   Diseases: {result_df['disease'].nunique()} - {sorted(result_df['disease'].unique())}")
    print(f"   Districts: {result_df['district'].nunique()}")
    
    return result_df


# Export for use in data_loader.py
load_pakpulse_csv_dataset = load_pakpulse_csv_optimized
