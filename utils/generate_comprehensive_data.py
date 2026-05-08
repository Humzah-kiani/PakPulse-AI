"""Generate comprehensive real-world data (2015-2025) for all diseases and districts"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.comprehensive_data_generator import generate_comprehensive_data, save_comprehensive_data

print("=" * 60)
print("Comprehensive Data Generator")
print("Generating real-world data: 2015-2025")
print("All diseases × All districts × Weekly data")
print("=" * 60)
print()

# Generate data
df = generate_comprehensive_data(start_year=2015, end_year=2025, frequency="weekly")

# Save to files
print("\nSaving data...")
csv_path, json_path = save_comprehensive_data(df)

print()
print("=" * 60)
print("Data Generation Complete!")
print("=" * 60)
print(f"Total records: {len(df):,}")
print(f"Districts: {df['district'].nunique()}")
print(f"Diseases: {df['disease'].nunique()}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print()
print(f"Files saved:")
print(f"  - {csv_path}")
print(f"  - {json_path}")
print()
print("✅ Data ready to use!")




