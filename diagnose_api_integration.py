#!/usr/bin/env python3
"""
PakPulse - API Integration Diagnostics Script
Comprehensive diagnostic tool to troubleshoot API integration issues
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DiagnosticReport:
    """Generate comprehensive diagnostic report"""
    
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "database": {},
            "apis": {},
            "logs": {},
            "recommendations": []
        }
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("Checking Python version...")
        version = sys.version_info
        self.report["system"]["python_version"] = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.report["recommendations"].append(
                "⚠ Python 3.8+ required. Current version is too old."
            )
            return False
        
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_installed_packages(self):
        """Check if required packages are installed"""
        print("\nChecking installed packages...")
        
        required_packages = [
            'psycopg2',
            'requests',
            'boto3',
            'pandas',
            'python-dotenv',
            'schedule'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✓ {package} installed")
            except ImportError:
                print(f"✗ {package} NOT installed")
                missing_packages.append(package)
        
        if missing_packages:
            self.report["recommendations"].append(
                f"Install missing packages: pip install {' '.join(missing_packages)}"
            )
        
        return len(missing_packages) == 0
    
    def check_environment_variables(self):
        """Check all environment variables"""
        print("\nChecking environment variables...")
        
        required_vars = {
            "database": ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"],
            "openweather": ["OPENWEATHER_API_KEY"],
            "aws": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
        }
        
        all_set = True
        
        for category, vars_list in required_vars.items():
            print(f"\n  {category.upper()}:")
            for var in vars_list:
                value = os.getenv(var)
                if value:
                    # Mask sensitive values
                    if any(x in var for x in ["KEY", "PASSWORD", "SECRET"]):
                        masked = value[:3] + "*" * (len(value) - 6) + value[-3:]
                    else:
                        masked = value
                    print(f"    ✓ {var} = {masked}")
                else:
                    print(f"    ✗ {var} = NOT SET")
                    all_set = False
        
        self.report["environment"] = {
            "required_vars_set": all_set,
            "missing_count": sum(1 for cat, vars_list in required_vars.items() 
                                for var in vars_list if not os.getenv(var))
        }
        
        return all_set
    
    def check_database_connection(self):
        """Test PostgreSQL connection"""
        print("\nChecking database connection...")
        
        try:
            import psycopg2
            from psycopg2 import OperationalError
            
            conn_params = {
                'host': os.getenv('DB_HOST'),
                'port': os.getenv('DB_PORT', 5432),
                'database': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD')
            }
            
            try:
                conn = psycopg2.connect(**conn_params)
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    print(f"✓ Connected to: {version[0][:60]}...")
                    
                    # Check tables
                    cursor.execute("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    tables = [t[0] for t in cursor.fetchall()]
                    
                    required_tables = ["districts", "diseases", "disease_cases", 
                                     "weather_data", "api_logs"]
                    
                    self.report["database"]["connected"] = True
                    self.report["database"]["tables"] = {
                        table: table in tables for table in required_tables
                    }
                    
                    missing_tables = [t for t in required_tables if t not in tables]
                    if missing_tables:
                        self.report["recommendations"].append(
                            f"Create missing tables: {', '.join(missing_tables)}"
                        )
                    
                    print(f"✓ Found {len(tables)} tables")
                    for table in required_tables:
                        if table in tables:
                            print(f"  ✓ {table}")
                        else:
                            print(f"  ✗ {table} (MISSING)")
                
                conn.close()
                return True
            
            except OperationalError as e:
                print(f"✗ Connection failed: {str(e)}")
                self.report["database"]["connected"] = False
                self.report["database"]["error"] = str(e)
                self.report["recommendations"].append(
                    "Ensure PostgreSQL is running and credentials are correct"
                )
                return False
        
        except ImportError:
            print("✗ psycopg2 not installed")
            self.report["recommendations"].append("Install psycopg2: pip install psycopg2-binary")
            return False
    
    def check_openweather_api(self):
        """Test OpenWeather API connectivity"""
        print("\nChecking OpenWeather API...")
        
        api_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not api_key:
            print("✗ OpenWeather API key not configured")
            self.report["recommendations"].append(
                "Add OPENWEATHER_API_KEY to .env file"
            )
            return False
        
        try:
            import requests
            
            # Test API call
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': 31.5497,
                'lon': 74.3436,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ API call successful")
                print(f"  ✓ Current temp in Lahore: {data['main']['temp']}°C")
                print(f"  ✓ Humidity: {data['main']['humidity']}%")
                self.report["apis"]["openweather"] = {
                    "status": "OK",
                    "temperature": data['main']['temp'],
                    "humidity": data['main']['humidity']
                }
                return True
            elif response.status_code == 401:
                print(f"✗ API key invalid (401)")
                self.report["recommendations"].append(
                    "Check OpenWeather API key validity"
                )
                return False
            elif response.status_code == 429:
                print(f"✗ Rate limit exceeded (429)")
                self.report["recommendations"].append(
                    "Rate limited. Wait before retrying."
                )
                return False
            else:
                print(f"✗ API error: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"✗ API test failed: {str(e)}")
            self.report["apis"]["openweather"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def check_gho_api(self):
        """Test WHO GHO API"""
        print("\nChecking WHO GHO API...")
        
        try:
            import requests
            
            url = "https://www.who.int/data/gho/api/Indicator"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ API accessible")
                self.report["apis"]["gho"] = {"status": "OK"}
                return True
            else:
                print(f"✗ API error: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"✗ API test failed: {str(e)}")
            self.report["apis"]["gho"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def check_aws_credentials(self):
        """Test AWS credentials validity"""
        print("\nChecking AWS credentials...")
        
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not (aws_key and aws_secret):
            print("⚠ AWS credentials not configured (optional)")
            return None
        
        try:
            import boto3
            
            client = boto3.client(
                'sts',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret
            )
            
            identity = client.get_caller_identity()
            print(f"✓ AWS credentials valid")
            print(f"  Account ID: {identity['Account']}")
            print(f"  ARN: {identity['Arn']}")
            self.report["apis"]["aws"] = {
                "status": "OK",
                "account_id": identity['Account']
            }
            return True
        
        except Exception as e:
            print(f"✗ AWS credentials invalid: {str(e)}")
            self.report["apis"]["aws"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
    
    def check_recent_logs(self):
        """Check recent API call logs"""
        print("\nChecking recent API call logs...")
        
        try:
            from db_config import DatabaseConnection
            
            db = DatabaseConnection()
            
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get logs from last 24 hours
                    cursor.execute("""
                        SELECT api_name, COUNT(*) as calls, 
                               SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as successful,
                               AVG(response_time_ms) as avg_response
                        FROM api_logs
                        WHERE request_timestamp > NOW() - INTERVAL '24 hours'
                        GROUP BY api_name
                    """)
                    
                    logs = cursor.fetchall()
                    
                    if logs:
                        print("✓ Recent API calls found:")
                        self.report["logs"]["last_24_hours"] = {}
                        
                        for api_name, calls, successful, avg_response in logs:
                            success_rate = (successful / calls * 100) if calls > 0 else 0
                            print(f"  {api_name}: {calls} calls, {success_rate:.1f}% successful, {avg_response:.0f}ms avg")
                            self.report["logs"]["last_24_hours"][api_name] = {
                                "calls": calls,
                                "successful": successful,
                                "success_rate": success_rate,
                                "avg_response_ms": avg_response
                            }
                    else:
                        print("⚠ No recent API calls found")
                    
                    # Get latest errors
                    cursor.execute("""
                        SELECT api_name, error_message, COUNT(*) as count, MAX(request_timestamp) as last_error
                        FROM api_logs
                        WHERE status_code != 200 AND request_timestamp > NOW() - INTERVAL '7 days'
                        GROUP BY api_name, error_message
                        LIMIT 5
                    """)
                    
                    errors = cursor.fetchall()
                    
                    if errors:
                        print("\n✗ Recent errors:")
                        for api_name, error_msg, count, last_error in errors:
                            print(f"  {api_name}: {error_msg} (×{count}, last: {last_error})")
            
            return True
        
        except Exception as e:
            print(f"✗ Could not check logs: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate final diagnostic report"""
        print("\n" + "=" * 70)
        print("DIAGNOSTIC REPORT")
        print("=" * 70)
        
        print(json.dumps(self.report, indent=2, default=str))
        
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        
        if self.report["recommendations"]:
            for i, rec in enumerate(self.report["recommendations"], 1):
                print(f"{i}. {rec}")
        else:
            print("✓ No issues detected - system is ready!")
        
        print("\n" + "=" * 70)
        print(f"Report generated: {self.report['timestamp']}")
        print("=" * 70)
        
        # Save report to file
        report_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2, default=str)
        print(f"\nReport saved to: {report_file}")


def main():
    """Run all diagnostics"""
    print("=" * 70)
    print("PakPulse - API Integration Diagnostics")
    print("=" * 70)
    
    diagnostics = DiagnosticReport()
    
    # Run all checks
    diagnostics.check_python_version()
    diagnostics.check_installed_packages()
    diagnostics.check_environment_variables()
    diagnostics.check_database_connection()
    diagnostics.check_openweather_api()
    diagnostics.check_gho_api()
    diagnostics.check_aws_credentials()
    diagnostics.check_recent_logs()
    
    # Generate report
    diagnostics.generate_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
