#!/usr/bin/env python
"""
Setup and Demo Script for PakPulse Database Integration
"""

import os
import sys

print("=" * 70)
print("PakPulse Database Integration - Setup & Demo")
print("=" * 70)

print("\n[1] Checking Python environment...")
print(f"Python Version: {sys.version.split()[0]}")
print(f"Working Directory: {os.getcwd()}")

# Test imports
print("\n[2] Checking package imports...")
required_packages = {
    'psycopg2': 'Database connection',
    'dotenv': 'Configuration management',
    'requests': 'API requests',
    'boto3': 'AWS services',
    'schedule': 'Job scheduling',
    'pandas': 'Data processing',
    'numpy': 'Numerical computing'
}

missing_packages = []
for package, description in required_packages.items():
    try:
        __import__(package)
        print(f"  ✓ {package:20} - {description}")
    except ImportError:
        print(f"  ✗ {package:20} - {description} (MISSING)")
        missing_packages.append(package)

if missing_packages:
    print(f"\nMissing packages: {', '.join(missing_packages)}")
else:
    print("\n✓ All packages installed successfully!")

# Create configuration file
print("\n[3] Creating .env configuration...")
env_content = """# PakPulse Database Integration Configuration

# Database (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pakpulse_db
DB_USER=postgres
DB_PASSWORD=postgres

# OpenWeather API
OPENWEATHER_API_KEY=demo_key_replace_with_yours

# AWS Athena (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
ATHENA_S3_OUTPUT_LOCATION=s3://pakpulse-athena-results/

# Pipeline Settings
PIPELINE_RUN_FREQUENCY=daily
PIPELINE_LOG_LEVEL=INFO
"""

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write(env_content)
    print("  ✓ Created .env configuration file")
else:
    print("  ✓ .env file already exists")

# Quick start guide
print("\n" + "=" * 70)
print("QUICK START GUIDE")
print("=" * 70)
print("""
Step 1: Install PostgreSQL
  - Download from: https://www.postgresql.org/download/windows/
  - Run installer, remember the password
  
Step 2: Create the database schema
  - Open Command Prompt/PowerShell
  - Run: psql -U postgres -f database_schema.sql
  - Enter your PostgreSQL password when prompted
  
Step 3: Initialize sample data
  - Run: python init_sample_data.py
  
Step 4: Configure API keys (Optional)
  - Edit .env file with your API keys:
    * OpenWeather: https://openweathermap.org/api
    * AWS: https://console.aws.amazon.com/
  
Step 5: Run the data pipeline
  - python data_pipeline.py

Available Modules:
  - db_config.py: Database connection & CRUD operations
  - openweather_api.py: Weather data fetching
  - gho_api.py: WHO health indicators
  - athena_api.py: AWS Athena disease data
  - data_pipeline.py: Main orchestrator
  
Database Tables:
  - districts: Location and demographic data
  - diseases: Disease definitions
  - weather_data: Temperature, humidity, rainfall
  - disease_cases: Case counts and statistics
  - health_indicators: WHO health data
  - predictions: ML model predictions
  - api_logs: API call tracking
  - data_sync_logs: Sync operation logs
""")

# Print file status
print("\n" + "=" * 70)
print("FILES CREATED")
print("=" * 70)

files = [
    'db_config.py',
    'openweather_api.py',
    'gho_api.py',
    'athena_api.py',
    'data_pipeline.py',
    'database_schema.sql',
    '.env',
    'requirements_integration.txt',
    'DATABASE_INTEGRATION_README.md',
]

for fname in files:
    exists = "✓" if os.path.exists(fname) else "✗"
    print(f"  {exists} {fname}")

print("\n" + "=" * 70)
print("SETUP COMPLETE")
print("=" * 70)
print("""
Next Steps:
1. Install PostgreSQL from https://www.postgresql.org/
2. Run: psql -U postgres -f database_schema.sql
3. Run: python init_sample_data.py
4. Run: python data_pipeline.py

For complete documentation, see: DATABASE_INTEGRATION_README.md
""")
