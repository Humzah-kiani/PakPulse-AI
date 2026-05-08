import pandas as pd

# Load the dataset
df = pd.read_csv('pakpulse_250k_featured.csv')

# Get all unique districts
districts = sorted(df['district'].unique())

print(f"Total districts: {len(districts)}")
print("\nAll districts:")
for i, district in enumerate(districts, 1):
    print(f"{i:2d}. {district}")

# Get sample coordinates for each district (using first occurrence)
print("\n\nDistrict coordinates (sample from dataset):")
district_coords = {}
for district in districts:
    sample_row = df[df['district'] == district].iloc[0]
    lat = sample_row.get('latitude', 30.0)  # Default if not available
    lon = sample_row.get('longitude', 70.0)
    district_coords[district] = (lat, lon)
    print(f"{district}: {lat:.4f}, {lon:.4f}")