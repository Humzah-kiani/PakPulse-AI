#!/usr/bin/env python3
"""Debug heatmap data rendering"""

import pandas as pd
from datetime import datetime
from src.data_loader import load_pakpulse_csv_dataset
from src.gis_map import GISMap

print("="*80)
print("HEATMAP DATA DEBUGGING")
print("="*80)

# Load data
print("\n1. Loading data...")
df = load_pakpulse_csv_dataset()
print(f"   Loaded: {len(df):,} records")
print(f"   Diseases: {df['disease'].nunique()}")
print(f"   Districts: {df['district'].nunique()}")

# Get latest date data
latest_date = df['date'].max()
latest_data = df[df['date'] == latest_date]
print(f"\n2. Latest date data:")
print(f"   Date: {latest_date}")
print(f"   Records on this date: {len(latest_data)}")

# Check risk distribution
print(f"\n3. Risk Index Distribution:")
print(f"   Min: {df['risk_index'].min():.2f}")
print(f"   Max: {df['risk_index'].max():.2f}")
print(f"   Mean: {df['risk_index'].mean():.2f}")
print(f"   Median: {df['risk_index'].median():.2f}")

# Check grouping
grouped = latest_data.groupby(['district', 'disease']).first().reset_index()
print(f"\n4. Unique district-disease combos on latest date: {len(grouped)}")

# Prepare heatmap data manually to see what it looks like
heat_data = []
for _, row in grouped.iterrows():
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    risk = float(row['risk_index'])
    weight = max(0, min(1, risk / 50.0))
    weight = max(0.1, weight)
    heat_data.append([lat, lon, weight])

print(f"\n5. Heatmap Layer Data:")
print(f"   Total points: {len(heat_data)}")
print(f"   Sample points (first 5):")
for i, point in enumerate(heat_data[:5]):
    print(f"     [{point[0]:.4f}, {point[1]:.4f}, weight={point[2]:.3f}]")

# Check weight distribution
weights = [p[2] for p in heat_data]
print(f"\n   Weight statistics:")
print(f"   Min weight: {min(weights):.3f}")
print(f"   Max weight: {max(weights):.3f}")
print(f"   Mean weight: {sum(weights)/len(weights):.3f}")

# Check for duplicate locations
locations = [(p[0], p[1]) for p in heat_data]
unique_locations = set(locations)
print(f"\n6. Location uniqueness:")
print(f"   Total points: {len(heat_data)}")
print(f"   Unique locations: {len(unique_locations)}")

# Try creating the heatmap
print(f"\n7. Creating test heatmap...")
try:
    gis = GISMap()
    
    # Filter to single disease for testing
    single_disease = latest_data[latest_data['disease'] == 'COVID-19'].copy()
    print(f"   Testing with {single_disease['disease'].nunique()} disease(s)")
    print(f"   Records: {len(single_disease)}")
    
    # Get latest for this disease
    grouped_disease = single_disease.groupby(['district']).first().reset_index()
    print(f"   Unique districts: {len(grouped_disease)}")
    
    # Create heatmap
    m = gis.create_risk_heatmap(single_disease, disease_filter='COVID-19')
    print(f"   Heatmap created: {m is not None}")
    
    # Save for inspection
    m.save('/tmp/test_heatmap.html')
    print(f"   Saved to: /tmp/test_heatmap.html")
    
except Exception as e:
    print(f"   ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("END DEBUG")
print("="*80)
