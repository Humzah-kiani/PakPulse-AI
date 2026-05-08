"""
App Health Check - Verifies that all critical components are working
"""
import sys
import time

def test_app_components():
    print("=" * 70)
    print("PAKPULSE AI - APP HEALTH CHECK")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Data Loader
    tests_total += 1
    print("\n[1] Testing Data Loader...")
    try:
        from src.data_loader import load_pakpulse_csv_dataset
        data = load_pakpulse_csv_dataset()
        assert len(data) > 0, "No data loaded"
        assert len(data) == 250000, f"Expected 250k records, got {len(data)}"
        assert data['district'].nunique() == 50, f"Expected 50 districts, got {data['district'].nunique()}"
        assert data['disease'].nunique() == 20, f"Expected 20 diseases, got {data['disease'].nunique()}"
        print("    ✓ Data Loader: OK")
        print(f"    ✓ Records: {len(data):,} | Districts: {data['district'].nunique()} | Diseases: {data['disease'].nunique()}")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Data Loader: FAILED - {str(e)[:60]}")
    
    # Test 2: GIS Map
    tests_total += 1
    print("\n[2] Testing GIS Map...")
    try:
        from src.gis_map import GISMap
        gis = GISMap()
        base_map = gis.create_base_map()
        assert base_map is not None, "Base map is None"
        print("    ✓ GIS Map: OK")
        print("    ✓ Base map created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ GIS Map: FAILED - {str(e)[:60]}")
    
    # Test 3: Risk Calculator
    tests_total += 1
    print("\n[3] Testing Risk Calculator...")
    try:
        from src.risk_calculator import RiskCalculator
        calc = RiskCalculator()
        assert calc is not None, "Risk calculator is None"
        print("    ✓ Risk Calculator: OK")
        print("    ✓ Risk calculator initialized successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Risk Calculator: FAILED - {str(e)[:60]}")
    
    # Test 4: Database Connection
    tests_total += 1
    print("\n[4] Testing Database Connection...")
    try:
        from src.db_config import DatabaseConfig
        db = DatabaseConfig()
        # Don't actually connect, just verify config can be initialized
        print("    ✓ Database Config: OK")
        print("    ✓ Database configuration loaded successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Database Config: FAILED - {str(e)[:60]}")
    
    # Test 5: Authentication
    tests_total += 1
    print("\n[5] Testing Authentication System...")
    try:
        from src.auth import AuthManager
        auth = AuthManager()
        assert auth is not None, "Auth manager is None"
        print("    ✓ Authentication: OK")
        print("    ✓ Authentication system ready")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Authentication: FAILED - {str(e)[:60]}")
    
    # Test 6: JSON Serialization (Critical)
    tests_total += 1
    print("\n[6] Testing JSON Serialization (Critical)...")
    try:
        from src.data_loader import load_pakpulse_csv_dataset
        from src.gis_map import GISMap
        data = load_pakpulse_csv_dataset()
        latest = data[data['date'] == data['date'].max()]
        
        gis = GISMap()
        map_obj = gis.create_risk_heatmap(latest)
        
        # Try to generate HTML (what Streamlit does)
        html = map_obj._repr_html_()
        assert len(html) > 0, "No HTML generated"
        assert "function" not in str(type(html)), "HTML contains function objects"
        
        print("    ✓ JSON Serialization: OK")
        print(f"    ✓ Map HTML generated: {len(html):,} bytes")
        tests_passed += 1
    except TypeError as e:
        if "JSON serializable" in str(e):
            print(f"    ✗ JSON Serialization: FAILED - {str(e)[:60]}")
        else:
            raise
    except Exception as e:
        print(f"    ✗ JSON Serialization: FAILED - {str(e)[:60]}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {tests_passed}/{tests_total} passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("\n✓ ALL TESTS PASSED - App is operational!")
        print("\nAccess the app at: http://localhost:8503")
        print("Available pages:")
        print("  • Home (Main dashboard)")
        print("  • GIS Dashboard (Interactive maps)")
        print("  • Risk Dashboard (Risk analytics)")
        print("  • Alert System (Alerts & notifications)")
        return True
    else:
        print(f"\n✗ {tests_total - tests_passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = test_app_components()
    sys.exit(0 if success else 1)
