#!/usr/bin/env python3
"""Test risk index calculation"""

from src.data_loader import load_pakpulse_csv_dataset

print("Loading data with recalibrated risk thresholds...")
df = load_pakpulse_csv_dataset()

print(f'\nRisk Index Statistics:')
print(f'  Min: {df["risk_index"].min():.1f}')
print(f'  Max: {df["risk_index"].max():.1f}')
print(f'  Mean: {df["risk_index"].mean():.1f}')
print(f'  Median: {df["risk_index"].median():.1f}')
print(f'  Std Dev: {df["risk_index"].std():.1f}')

print(f'\nDisease Risk Distribution (max values):')
for d in sorted(df['disease'].unique()):
    disease_data = df[df["disease"] == d]
    max_risk = disease_data["risk_index"].max()
    mean_risk = disease_data["risk_index"].mean()
    print(f'  {d:20s}: max={max_risk:5.1f}, mean={mean_risk:5.1f}')

print(f'\nSample risky records:')
high_risk = df[df["risk_index"] > 50].sort_values("risk_index", ascending=False).head(10)
print(high_risk[['district', 'disease', 'cases_reported', 'risk_index', 'date']].to_string())
