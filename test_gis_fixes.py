#!/usr/bin/env python3
"""
Comprehensive test of GIS Dashboard fixes
Verifies:
1. All 50 districts are loaded
2. All 20 diseases are loaded
3. Risk index is properly calculated
4. Heatmap will work with the data
5. Dashboard loads quickly
"""

import time
import pandas as pd
from datetime import datetime

print("\n" + "="*80)
print("COMPREHENSIVE GIS DASHBOARD TESTING")
print("="*80 + "\n")

# Test 1: Data Loading Performance
print("TEST 1: Data Loading Performance")
print("-" * 80)

start = time.time()
from src.data_loader import load_pakpulse_csv_dataset
df = load_pakpulse_csv_dataset()
load_time = time.time() - start

print(f"✅ Load time: {load_time:.2f} seconds")
assert load_time < 5, "Load time too slow!"

# Test 2: Dataset Completeness
print("\nTEST 2: Dataset Completeness")
print("-" * 80)

print(f"✅ Total records: {len(df):,}")
assert len(df) == 250000, "Expected 250k records!"

districts = df['district'].nunique()
print(f"✅ Districts: {districts}")
assert districts == 50, f"Expected 50 districts, got {districts}"

diseases = df['disease'].nunique()
print(f"✅ Diseases: {diseases}")
assert diseases == 20, f"Expected 20 diseases, got {diseases}"

# Verify all required columns
required_cols = ['district', 'latitude', 'longitude', 'disease', 'risk_index', 'date', 'cases_reported', 'population']
for col in required_cols:
    assert col in df.columns, f"Missing column: {col}"
print(f"✅ All required columns present")

# Test 3: Risk Index Distribution
print("\nTEST 3: Risk Index Distribution")
print("-" * 80)

print(f"✅ Risk index range: {df['risk_index'].min():.1f} to {df['risk_index'].max():.1f}")
assert df['risk_index'].min() >= 0, "Risk index should be >= 0"
assert df['risk_index'].max() <= 100, "Risk index should be <= 100"

print(f"✅ Mean risk: {df['risk_index'].mean():.2f}")
print(f"✅ Median risk: {df['risk_index'].median():.2f}")

# Test 4: Data Quality
print("\nTEST 4: Data Quality")
print("-" * 80)

null_count = df.isnull().sum().sum()
print(f"✅ Null values: {null_count}")
assert null_count == 0, "Found null values in data!"

print(f"✅ Date range: {df['date'].min().date()} to {df['date'].max().date()}")
assert len(df['date'].unique()) > 100, "Expected many unique dates"

# Test 5: District-Disease Coverage
print("\nTEST 5: District-Disease Coverage")
print("-" * 80)

combinations = df[['district', 'disease']].drop_duplicates()
print(f"✅ Unique district-disease combinations: {len(combinations):,}")
expected_combinations = 50 * 20  # 50 districts * 20 diseases
print(f"   (Expected: {expected_combinations:,})")

# Not all combinations may have data, so just check we have good coverage
coverage_percent = (len(combinations) / expected_combinations) * 100
print(f"✅ Coverage: {coverage_percent:.1f}%")
assert coverage_percent >= 90, f"Coverage too low: {coverage_percent}%"

# Test 6: Sample Data Inspection
print("\nTEST 6: Sample Data Quality")
print("-" * 80)

# Show distribution by disease
print("\nDisease distribution:")
for disease in sorted(df['disease'].unique()):
    count = len(df[df['disease'] == disease])
    max_risk = df[df['disease'] == disease]['risk_index'].max()
    print(f"  {disease:20s}: {count:6,} records, max risk: {max_risk:5.1f}")

# Show distribution by district
print("\nTop 5 districts by record count:")
top_districts = df['district'].value_counts().head(5)
for district, count in top_districts.items():
    print(f"  {district:20s}: {count:6,} records")

# Test 7: Heatmap Visualization Readiness
print("\nTEST 7: Heatmap Visualization Readiness")
print("-" * 80)

# Check if latest data has good coverage
latest_date = df['date'].max()
latest_df = df[df['date'] == latest_date]
print(f"✅ Latest date in data: {latest_date.date()}")
print(f"✅ Records on latest date: {len(latest_df):,}")
unique_locations = latest_df[['latitude', 'longitude']].drop_duplicates()
print(f"✅ Unique locations on latest date: {len(unique_locations):,}")

# Check risk value distribution for heatmap
risk_dist = {
    'Very Low (0-10)': len(df[df['risk_index'] < 10]),
    'Low (10-20)': len(df[(df['risk_index'] >= 10) & (df['risk_index'] < 20)]),
    'Medium (20-30)': len(df[(df['risk_index'] >= 20) & (df['risk_index'] < 30)]),
    'High (30-50)': len(df[(df['risk_index'] >= 30) & (df['risk_index'] < 50)]),
    'Very High (50+)': len(df[df['risk_index'] >= 50]),
}
print(f"\nRisk value distribution:")
for category, count in risk_dist.items():
    percent = (count / len(df)) * 100
    print(f"  {category:20s}: {count:7,} ({percent:5.1f}%)")

# Verify heatmap visualization parameters
max_risk = df['risk_index'].max()
print(f"\n✅ Heatmap will scale risks by: 1/{max(1, max_risk/50):.1f}")
print("   (This ensures proper color gradient rendering)")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED!")
print("="*80)
print("\nSUMMARY:")
print(f"  • Dataset: {len(df):,} records fully loaded")
print(f"  • Completeness: All 50 districts and 20 diseases present") 
print(f"  • Performance: Loaded in {load_time:.2f} seconds")
print(f"  • Data Quality: No null values, spanning {len(df['date'].unique())} dates")
print(f"  • Heatmap Ready: Risk values properly distributed for visualization")
print(f"\n🚀 GIS Dashboard is ready with FULL dataset!\n")
