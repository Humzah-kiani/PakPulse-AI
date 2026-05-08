#!/usr/bin/env python3
"""Check CSV data to diagnose dashboard loading issues"""

import pandas as pd

print("=" * 80)
print("CHECKING CSV DATA COMPLETENESS")
print("=" * 80)

df = pd.read_csv('pakpulse_250k_realistic.csv', low_memory=False)

print(f"\nTotal records: {len(df):,}")
print(f"Columns: {list(df.columns)}")

print(f"\n--- DISTRICTS ---")
unique_districts = df['district'].nunique()
print(f"Unique districts: {unique_districts}")
print(f"Districts list: {sorted(df['district'].unique())}")

print(f"\n--- DISEASES ---")
unique_diseases = df['disease'].nunique()
print(f"Unique diseases: {unique_diseases}")
print(f"Diseases list: {sorted(df['disease'].unique())}")

print(f"\n--- DATE RANGE ---")
print(f"Date column dtype: {df['date'].dtype}")
df['date'] = pd.to_datetime(df['date'])
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

print(f"\n--- DATA SAMPLE ---")
print(df.head())

print(f"\n--- MEMORY USAGE ---")
print(f"DataFrame size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print(f"\n--- DATA QUALITY ---")
print(f"Null values:\n{df.isnull().sum()}")

print(f"\n--- DISTRIBUTION ---")
print(f"Records per district: {len(df) // unique_districts:.0f} (approx)")
print(f"Records per disease: {len(df) // unique_diseases:.0f} (approx)")
print(f"Records per district-disease combo: {len(df) // (unique_districts * unique_diseases):.1f} (approx)")
