#!/usr/bin/env python3
"""Test optimized data loading"""

import time
import sys

print("\n" + "="*80)
print("TESTING OPTIMIZED DATA LOADING")
print("="*80 + "\n")

start_time = time.time()

try:
    from src.data_loader import load_pakpulse_csv_dataset
    
    print("Loading CSV data with optimized function...")
    df = load_pakpulse_csv_dataset()
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}\n")
    
    print(f"✓ Load time: {elapsed:.2f} seconds")
    print(f"✓ Total records: {len(df):,}")
    print(f"✓ Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
    
    print(f"DISTRICTS: {df['district'].nunique()}")
    districts = sorted(df['district'].unique())
    for i, d in enumerate(districts, 1):
        if i % 5 == 0:
            print(f"  {i:2d}. {d}")
        else:
            print(f"  {i:2d}. {d}")
    
    print(f"\nDISEASES: {df['disease'].nunique()}")
    diseases = sorted(df['disease'].unique())
    for i, d in enumerate(diseases, 1):
        print(f"  {i:2d}. {d}")
    
    print(f"\nDATA QUALITY:")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Risk index range: {df['risk_index'].min():.1f} to {df['risk_index'].max():.1f}")
    print(f"  Null values: {df.isnull().sum().sum()} total")
    
    print(f"\nDISTRICT-DISEASE DISTRIBUTION:")
    print(f"  Records per district: ~{len(df) // df['district'].nunique():.0f}")
    print(f"  Records per disease: ~{len(df) // df['disease'].nunique():.0f}")
    print(f"  Records per district-disease: ~{len(df) // (df['district'].nunique() * df['disease'].nunique()):.0f}")
    
    # Show some sample data
    print(f"\nSAMPLE DATA (first 10 rows):")
    print(df[['district', 'disease', 'date', 'risk_index', 'cases_reported']].head(10).to_string())
    
    # Verify we have all required columns
    required_cols = ['district', 'latitude', 'longitude', 'disease', 'risk_index', 'date', 'cases_reported', 'population']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        print(f"\n❌ ERROR: Missing required columns: {missing_cols}")
        sys.exit(1)
    else:
        print(f"\n✅ All required columns present!")
    
    print(f"\n{'='*80}")
    print(f"✅ TESTING PASSED - Data is ready for dashboard!")
    print(f"{'='*80}\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
