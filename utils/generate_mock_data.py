"""
Utility script to generate mock disease risk data for PakPulse AI
Creates sample data for multiple diseases across Pakistani districts
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import random

# Major Pakistani districts with approximate coordinates (lat, lon)
DISTRICTS = {
    "Karachi": (24.8607, 67.0011),
    "Lahore": (31.5204, 74.3587),
    "Islamabad": (33.6844, 73.0479),
    "Faisalabad": (31.4504, 73.1350),
    "Rawalpindi": (33.5651, 73.0169),
    "Multan": (30.1575, 71.5249),
    "Peshawar": (34.0151, 71.5249),
    "Quetta": (30.1798, 66.9750),
    "Sialkot": (32.4945, 74.5229),
    "Gujranwala": (32.1617, 74.1883),
    "Hyderabad": (25.3960, 68.3578),
    "Sargodha": (32.0836, 72.6711),
    "Bahawalpur": (29.4000, 71.6833),
    "Sukkur": (27.7032, 68.8589),
    "Larkana": (27.5590, 68.2120),
    "Sheikhupura": (31.7167, 73.9833),
    "Jhang": (31.2800, 72.3317),
    "Rahim Yar Khan": (28.4212, 70.2989),
    "Gujrat": (32.5739, 74.0776),
    "Kasur": (31.1167, 74.4500),
}

# Diseases to include (11 total)
DISEASES = [
    "dengue", "malaria", "cholera", "influenza", "covid19",
    "monkeypox", "hepatitis_a", "hepatitis_e", "typhoid", "tuberculosis", "meningitis"
]

# Generate dates for the last 3 months
def generate_dates(start_date, days=90):
    """Generate list of dates"""
    return [start_date + timedelta(days=x) for x in range(0, days, 7)]  # Weekly data

def generate_risk_index(district, disease, date):
    """
    Generate realistic risk index (0-100) based on:
    - Disease type (some diseases are more common in certain areas)
    - District (urban vs rural, climate factors)
    - Seasonal patterns (date-based)
    """
    base_risk = random.randint(20, 80)
    
    # Disease-specific adjustments
    if disease == "dengue":
        # Higher in urban areas like Karachi, Lahore
        if district in ["Karachi", "Lahore", "Faisalabad"]:
            base_risk += random.randint(10, 20)
        # Seasonal: higher in monsoon season (July-September)
        if date.month in [7, 8, 9]:
            base_risk += random.randint(5, 15)
    
    elif disease == "malaria":
        # Higher in rural/agricultural areas
        if district in ["Multan", "Bahawalpur", "Rahim Yar Khan"]:
            base_risk += random.randint(10, 20)
        # Seasonal: higher in rainy season
        if date.month in [7, 8, 9, 10]:
            base_risk += random.randint(5, 15)
    
    elif disease == "cholera":
        # Higher in areas with poor sanitation
        if district in ["Larkana", "Sukkur", "Hyderabad"]:
            base_risk += random.randint(10, 20)
        # Higher in summer
        if date.month in [5, 6, 7, 8]:
            base_risk += random.randint(5, 15)
    
    elif disease == "influenza":
        # More common in winter months
        if date.month in [11, 12, 1, 2]:
            base_risk += random.randint(10, 20)
        # Higher in densely populated areas
        if district in ["Karachi", "Lahore", "Islamabad"]:
            base_risk += random.randint(5, 15)
    
    elif disease == "covid19":
        # Can vary, but generally lower now (post-pandemic)
        base_risk = random.randint(10, 40)
        # Slightly higher in major cities
        if district in ["Karachi", "Lahore", "Islamabad"]:
            base_risk += random.randint(5, 10)
    
    # Ensure risk is between 0-100
    return min(100, max(0, base_risk))

def generate_mock_data():
    """Generate mock disease risk data"""
    start_date = datetime.now() - timedelta(days=90)
    dates = generate_dates(start_date, days=90)
    
    data = []
    
    for district, (lat, lon) in DISTRICTS.items():
        for disease in DISEASES:
            for date in dates:
                risk_index = generate_risk_index(district, disease, date)
                
                data.append({
                    "district": district,
                    "latitude": lat,
                    "longitude": lon,
                    "disease": disease,
                    "risk_index": risk_index,
                    "date": date.strftime("%Y-%m-%d"),
                    "cases_reported": random.randint(0, 500) if risk_index > 50 else random.randint(0, 100),
                    "population": random.randint(500000, 5000000),
                })
    
    return pd.DataFrame(data)

def main():
    """Main function to generate and save mock data"""
    print("Generating mock disease risk data...")
    df = generate_mock_data()
    
    # Save as CSV
    csv_path = "data/disease_risk_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"[OK] Saved CSV data to {csv_path}")
    print(f"   Total records: {len(df)}")
    print(f"   Districts: {df['district'].nunique()}")
    print(f"   Diseases: {df['disease'].nunique()}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Save as JSON
    json_path = "data/disease_risk_data.json"
    df.to_json(json_path, orient="records", date_format="iso", indent=2)
    print(f"[OK] Saved JSON data to {json_path}")
    
    # Create districts metadata file
    districts_meta = []
    for district, (lat, lon) in DISTRICTS.items():
        districts_meta.append({
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "province": "Punjab" if district in ["Lahore", "Faisalabad", "Multan", "Sialkot", "Gujranwala", "Sargodha", "Bahawalpur", "Sheikhupura", "Jhang", "Rahim Yar Khan", "Gujrat", "Kasur"] else 
                       "Sindh" if district in ["Karachi", "Hyderabad", "Sukkur", "Larkana"] else
                       "Khyber Pakhtunkhwa" if district == "Peshawar" else
                       "Balochistan" if district == "Quetta" else
                       "Federal" if district == "Islamabad" else "Unknown"
        })
    
    districts_df = pd.DataFrame(districts_meta)
    districts_csv = "data/districts_metadata.csv"
    districts_df.to_csv(districts_csv, index=False)
    print(f"[OK] Saved districts metadata to {districts_csv}")
    
    # Save districts as JSON
    districts_json = "data/districts_metadata.json"
    districts_df.to_json(districts_json, orient="records", indent=2)
    print(f"[OK] Saved districts metadata JSON to {districts_json}")
    
    print("\nSample data preview:")
    print(df.head(10).to_string())
    
    print("\n[OK] Mock data generation complete!")

if __name__ == "__main__":
    main()

