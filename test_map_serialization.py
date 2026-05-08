"""
Test script to verify that the GIS map can be rendered without JSON serialization errors
"""
import sys
import pandas as pd
from src.data_loader import load_pakpulse_csv_dataset
from src.gis_map import GISMap

try:
    print("Loading dataset...")
    disease_data = load_pakpulse_csv_dataset()
    print(f"✓ Loaded {len(disease_data)} records")
    print(f"✓ Columns: {list(disease_data.columns)}")
    
    print("\nCreating GIS map...")
    gis = GISMap()
    
    # Test 1: Create base map
    print("Test 1: Creating base map...")
    m = gis.create_base_map()
    print("✓ Base map created successfully")
    
    # Test 2: Create heatmap
    print("Test 2: Creating heatmap...")
    m_heat = gis.create_risk_heatmap(disease_data)
    print("✓ Heatmap created successfully")
    
    # Test 3: Try to convert to JSON (this is what st_folium does)
    print("Test 3: Attempting JSON serialization...")
    import json
    try:
        # Get the map's HTML/JS content
        html = m_heat._repr_html_()
        print(f"✓ Map HTML generated successfully ({len(html)} bytes)")
    except TypeError as e:
        if "Object of type function is not JSON serializable" in str(e):
            print(f"✗ JSON serialization error: {e}")
            sys.exit(1)
        raise
    
    # Test 4: Check if we can access map data
    print("Test 4: Checking map data...")
    request = m_heat.to_dict()
    print(f"✓ Map data accessible (dict keys: {list(request.keys())})")
    
    print("\n✓ ALL TESTS PASSED - Map should display correctly in Streamlit!")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
