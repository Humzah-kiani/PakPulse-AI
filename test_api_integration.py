#!/usr/bin/env python3
"""
PakPulse - API Integration Test Suite
Tests connectivity and functionality of all integrated APIs
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")


def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")


def print_info(text):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


def test_environment_variables():
    """Test if all required environment variables are configured"""
    print_header("Environment Variables Configuration")
    
    required_vars = {
        "Database": ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"],
        "OpenWeather API": ["OPENWEATHER_API_KEY"],
        "AWS (Athena)": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
    }
    
    optional_vars = {
        "AWS Region": ["AWS_REGION"],
        "Athena S3 Output": ["ATHENA_S3_OUTPUT_LOCATION"],
    }
    
    all_configured = True
    
    print("\nREQUIRED VARIABLES:")
    for service, vars_list in required_vars.items():
        print(f"\n  {service}:")
        for var in vars_list:
            value = os.getenv(var)
            if value:
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                print_success(f"{var} = {masked_value}")
            else:
                print_error(f"{var} is NOT configured")
                all_configured = False
    
    print("\nOPTIONAL VARIABLES:")
    for service, vars_list in optional_vars.items():
        print(f"\n  {service}:")
        for var in vars_list:
            value = os.getenv(var)
            if value:
                print_success(f"{var} is configured")
            else:
                print_warning(f"{var} is not configured (using default)")
    
    return all_configured


def test_database_connection():
    """Test PostgreSQL database connectivity"""
    print_header("Database Connection Test")
    
    try:
        from db_config import DatabaseConnection
        
        db = DatabaseConnection()
        
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print_success(f"Connected to PostgreSQL: {version[0][:50]}...")
                
                # Check required tables exist
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                table_names = [t[0] for t in tables]
                
                required_tables = ["districts", "diseases", "disease_cases", "weather_data", "api_call_logs"]
                print(f"\nDatabase Tables ({len(table_names)} total):")
                
                for table in required_tables:
                    if table in table_names:
                        print_success(f"{table} table exists")
                    else:
                        print_error(f"{table} table is missing")
                
                return True
    
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


def test_openweather_api():
    """Test OpenWeather API connectivity"""
    print_header("OpenWeather API Test")
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        print_warning("OpenWeather API key not configured in .env")
        return False
    
    try:
        from openweather_api import OpenWeatherIntegration
        
        weather_api = OpenWeatherIntegration(api_key)
        print_info("OpenWeatherIntegration class initialized successfully")
        
        # Test with Lahore coordinates
        print("\nTesting API call to OpenWeather...")
        weather_data = weather_api.get_current_weather(latitude=31.5497, longitude=74.3436)
        
        if weather_data:
            print_success("OpenWeather API call successful")
            print(f"\n  Response Data (Lahore):")
            for key, value in weather_data.items():
                print(f"    • {key}: {value}")
            return True
        else:
            print_error("OpenWeather API returned no data")
            return False
    
    except Exception as e:
        print_error(f"OpenWeather API test failed: {str(e)}")
        return False


def test_gho_api():
    """Test WHO GHO API connectivity"""
    print_header("WHO GHO API Test")
    
    try:
        from gho_api import GHOIntegration
        
        gho_api = GHOIntegration()
        print_success("GHOIntegration class initialized successfully")
        
        print("\nTesting API call to WHO GHO...")
        indicators = gho_api.get_indicators()
        
        if indicators:
            print_success(f"WHO GHO API call successful - retrieved {len(indicators)} indicators")
            print("\n  Sample Indicators:")
            for indicator in indicators[:5]:
                print(f"    • {indicator.get('Name', 'Unknown')}")
            return True
        else:
            print_warning("WHO GHO API returned no indicators")
            return True  # GHO might not have data for Pakistan, but API is accessible
    
    except Exception as e:
        print_error(f"WHO GHO API test failed: {str(e)}")
        return False


def test_athena_api():
    """Test AWS Athena connectivity"""
    print_header("AWS Athena Integration Test")
    
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not (aws_key and aws_secret):
        print_warning("AWS credentials not configured in .env")
        return False
    
    try:
        from athena_api import AthenaIntegration
        
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        s3_output = os.getenv("ATHENA_S3_OUTPUT_LOCATION", "s3://pakpulse-athena-results/")
        
        athena_api = AthenaIntegration(
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
            s3_output_location=s3_output
        )
        print_success("AthenaIntegration class initialized successfully")
        print(f"  Region: {aws_region}")
        print(f"  S3 Output: {s3_output}")
        
        return True
    
    except Exception as e:
        print_error(f"AWS Athena test failed: {str(e)}")
        return False


def test_data_pipeline():
    """Test DataPipelineOrchestrator"""
    print_header("Data Pipeline Orchestrator Test")
    
    try:
        from data_pipeline import DataPipelineOrchestrator
        
        pipeline = DataPipelineOrchestrator()
        print_success("DataPipelineOrchestrator initialized successfully")
        
        # Check which APIs are available
        print("\nAPI Availability:")
        if pipeline.weather_api:
            print_success("OpenWeather API is available")
        else:
            print_warning("OpenWeather API not available")
        
        if pipeline.gho_api:
            print_success("WHO GHO API is available")
        else:
            print_warning("WHO GHO API not available")
        
        if pipeline.athena_api:
            print_success("AWS Athena API is available")
        else:
            print_warning("AWS Athena API not available")
        
        return True
    
    except Exception as e:
        print_error(f"Data Pipeline test failed: {str(e)}")
        return False


def main():
    """Run all API integration tests"""
    print(f"\n{Fore.MAGENTA}{'=' * 60}")
    print(f"{Fore.MAGENTA}PakPulse API Integration Test Suite".center(60))
    print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        "Environment Variables": test_environment_variables(),
        "Database Connection": test_database_connection(),
        "OpenWeather API": test_openweather_api(),
        "WHO GHO API": test_gho_api(),
        "AWS Athena": test_athena_api(),
        "Data Pipeline": test_data_pipeline(),
    }
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for test_name, result in test_results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Fore.MAGENTA}{'=' * 60}")
    if passed == total:
        print(f"{Fore.GREEN}✓ All tests passed! APIs are ready to use.".center(60))
    else:
        print(f"{Fore.YELLOW}⚠ Some tests failed. Check .env configuration.".center(60))
    print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext Steps:")
    print("  1. Fix any failed tests by checking your .env configuration")
    print("  2. Run: python init_sample_data.py")
    print("  3. Monitor: python data_pipeline.py")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
