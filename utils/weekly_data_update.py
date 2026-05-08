"""
Weekly Data Update Script for PakPulse AI
Fetches latest data from all APIs and updates the system
Can be run as a cron job for weekly updates
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def update_disease_data():
    """
    Fetch latest disease data from all APIs and save to storage
    """
    print("=" * 70)
    print(f"WEEKLY DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        from src.data_loader import load_combined_api_data
        
        # Fetch latest data
        print("\nFetching data from all APIs...")
        df = load_combined_api_data()
        
        if df.empty:
            print("⚠️  No data fetched")
            return False
        
        # Save to storage
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Save as CSV
        csv_path = data_dir / "disease_data_latest.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n✅ Data saved to: {csv_path}")
        print(f"   Records: {len(df):,}")
        print(f"   Diseases: {df['disease'].nunique()}")
        print(f"   Districts: {df['district'].nunique()}")
        
        # Save metadata
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "total_records": len(df),
            "diseases": sorted(df['disease'].unique().tolist()),
            "districts": sorted(df['district'].unique().tolist()),
            "year_range": {
                "min": int(df['date'].min().year) if 'date' in df.columns else None,
                "max": int(df['date'].max().year) if 'date' in df.columns else None
            }
        }
        
        metadata_path = data_dir / "data_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved to: {metadata_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_disease_data()
    sys.exit(0 if success else 1)



