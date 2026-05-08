#!/usr/bin/env python3
"""
PakPulse System - Component Test Script
Tests individual components without requiring full PostgreSQL setup
"""

import sys
import os
import traceback
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")

    tests = [
        ("db_config", "Database connection module"),
        ("openweather_api", "OpenWeather API integration"),
        ("gho_api", "WHO GHO API integration"),
        ("athena_api", "AWS Athena integration"),
        ("data_pipeline", "Data pipeline orchestrator")
    ]

    results = []
    for module_name, description in tests:
        try:
            __import__(module_name)
            results.append(f"✅ {description}")
            print(f"   ✓ {module_name}")
        except Exception as e:
            results.append(f"❌ {description}: {str(e)}")
            print(f"   ✗ {module_name}: {str(e)}")

    return results

def test_environment():
    """Test Python environment and packages"""
    print("\n🔍 Testing environment...")

    results = []

    # Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        results.append("✅ Python version 3.10+")
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        results.append(f"❌ Python version {version.major}.{version.minor} (need 3.10+)")
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro}")

    # Required packages
    packages = [
        ("psycopg2", "PostgreSQL driver"),
        ("dotenv", "Configuration management"),
        ("requests", "HTTP requests"),
        ("boto3", "AWS SDK"),
        ("schedule", "Job scheduling"),
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing")
    ]

    for package_name, description in packages:
        try:
            __import__(package_name)
            results.append(f"✅ {description}")
            print(f"   ✓ {package_name}")
        except ImportError:
            results.append(f"❌ {description} (not installed)")
            print(f"   ✗ {package_name}")

    return results

def test_configuration():
    """Test configuration file"""
    print("\n🔍 Testing configuration...")

    results = []

    env_file = ".env"
    if os.path.exists(env_file):
        results.append("✅ .env configuration file exists")
        print("   ✓ .env file found")

        # Check for required variables
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = [
            "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
            "OPENWEATHER_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"
        ]

        for var in required_vars:
            value = os.getenv(var)
            if value and value != "demo_key_replace_with_yours":
                results.append(f"✅ {var} configured")
                print(f"   ✓ {var}")
            else:
                results.append(f"⚠️  {var} not configured (demo value)")
                print(f"   ⚠ {var} (needs real value)")
    else:
        results.append("❌ .env configuration file missing")
        print("   ✗ .env file not found")

    return results

def test_files():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")

    required_files = [
        "database_schema.sql",
        "db_config.py",
        "openweather_api.py",
        "gho_api.py",
        "athena_api.py",
        "data_pipeline.py",
        "performance.py",
        "pakpulse_250k_featured.csv"
    ]

    results = []
    for filename in required_files:
        if os.path.exists(filename):
            results.append(f"✅ {filename}")
            print(f"   ✓ {filename}")
        else:
            results.append(f"❌ {filename} (missing)")
            print(f"   ✗ {filename}")

    return results

def test_api_connectivity():
    """Test API connectivity (without database)"""
    print("\n🔍 Testing API connectivity...")

    results = []

    # Test OpenWeather API (requires API key)
    try:
        from openweather_api import OpenWeatherIntegration
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key and api_key != "demo_key_replace_with_yours":
            api = OpenWeatherIntegration(api_key)
            # Test with sample coordinates (Lahore)
            weather = api.get_current_weather(31.5497, 74.3436)
            if weather:
                results.append("✅ OpenWeather API connection")
                print("   ✓ OpenWeather API")
            else:
                results.append("❌ OpenWeather API (no data returned)")
                print("   ✗ OpenWeather API (no data)")
        else:
            results.append("⚠️  OpenWeather API (API key needed)")
            print("   ⚠ OpenWeather API (API key needed)")
    except Exception as e:
        results.append(f"❌ OpenWeather API: {str(e)}")
        print(f"   ✗ OpenWeather API: {str(e)}")

    # Test GHO API (no authentication needed)
    try:
        from gho_api import GHOIntegration
        api = GHOIntegration()
        indicators = api.get_indicators()
        if indicators and len(indicators) > 0:
            results.append("✅ WHO GHO API connection")
            print("   ✓ WHO GHO API")
        else:
            results.append("❌ WHO GHO API (no data returned)")
            print("   ✗ WHO GHO API (no data)")
    except Exception as e:
        results.append(f"❌ WHO GHO API: {str(e)}")
        print(f"   ✗ WHO GHO API: {str(e)}")

    return results

def main():
    """Run all component tests"""
    print("=" * 60)
    print("🧪 PakPulse System - Component Test Suite")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    print()

    all_results = []

    # Run all tests
    test_functions = [
        test_environment,
        test_imports,
        test_files,
        test_configuration,
        test_api_connectivity
    ]

    for test_func in test_functions:
        try:
            results = test_func()
            all_results.extend(results)
        except Exception as e:
            print(f"   ✗ Test failed: {str(e)}")
            all_results.append(f"❌ {test_func.__name__}: {str(e)}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for r in all_results if r.startswith("✅"))
    warning_count = sum(1 for r in all_results if r.startswith("⚠️"))
    error_count = sum(1 for r in all_results if r.startswith("❌"))

    print(f"✅ Successful: {success_count}")
    print(f"⚠️  Warnings: {warning_count}")
    print(f"❌ Errors: {error_count}")
    print()

    # Detailed results
    for result in all_results:
        print(result)

    # Next steps
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)

    if error_count > 0:
        print("❌ Fix errors above before proceeding")
    else:
        print("✅ System components ready!")

    if "PostgreSQL" not in str(all_results):
        print("📋 Install PostgreSQL to run full pipeline:")
        print("   1. Download: https://www.postgresql.org/download/windows/")
        print("   2. Install with password 'pakpulse123'")
        print("   3. Run: psql -U postgres -f database_schema.sql")
        print("   4. Run: python data_pipeline.py")

    print("\n🚀 Ready to test the complete system!")

if __name__ == "__main__":
    main()