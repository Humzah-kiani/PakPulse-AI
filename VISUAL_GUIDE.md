# PakPulse Database Integration - Visual Guide

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                               │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │  OpenWeather   │  │ WHO GHO API  │  │ AWS Athena (S3) │     │
│  │   (Free API)   │  │  (Free API)  │  │  (Paid Query)   │     │
│  └────────┬───────┘  └──────┬───────┘  └────────┬────────┘     │
│           │                 │                   │              │
└───────────┼─────────────────┼───────────────────┼──────────────┘
            │                 │                   │
            ▼                 ▼                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              API INTEGRATION LAYER (Python)                      │
│  ┌────────────────────┐  ┌───────────────┐  ┌──────────────────┐│
│  │  openweather_api   │  │   gho_api     │  │  athena_api      ││
│  │                    │  │               │  │                  ││
│  │ • Fetch weather    │  │ • Health data │  │ • Query S3 data  ││
│  │ • Parse responses  │  │ • Risk factors│  │ • Sync to DB     ││
│  │ • Store in DB      │  │ • Indicators  │  │ • Outbreak detect││
│  └────────┬───────────┘  └────────┬──────┘  └────────┬─────────┘│
│           │                       │                  │          │
└───────────┼───────────────────────┼──────────────────┼──────────┘
            │                       │                  │
            └───────────┬───────────┴──────────────────┘
                        │
            ┌───────────▼────────────┐
            │  data_pipeline.py      │
            │                        │
            │ • Orchestrates all APIs│
            │ • Manages scheduling   │
            │ • Handles logging      │
            │ • Generates alerts     │
            └───────────┬────────────┘
                        │
            ┌───────────▼─────────────┐
            │  db_config.py           │
            │                         │
            │ • Connection pooling    │
            │ • CRUD operations       │
            │ • Transaction handling  │
            │ • Bulk operations       │
            └───────────┬─────────────┘
                        │
            ┌───────────▼──────────────────────────────────┐
            │      PostgreSQL Database                     │
            │     (pakpulse_db)                            │
            │                                              │
            │  ┌─────────────────────────────────────┐    │
            │  │ 8 Tables:                            │    │
            │  │ • districts (locations)              │    │
            │  │ • diseases (definitions)             │    │
            │  │ • weather_data (OpenWeather)         │    │
            │  │ • disease_cases (Athena)             │    │
            │  │ • health_indicators (GHO)            │    │
            │  │ • predictions (ML models)            │    │
            │  │ • api_logs (monitoring)              │    │
            │  │ • data_sync_logs (logging)           │    │
            │  └─────────────────────────────────────┘    │
            │                                              │
            │  ┌─────────────────────────────────────┐    │
            │  │ 2 Views:                             │    │
            │  │ • v_current_disease_status           │    │
            │  │ • v_outbreak_risk                    │    │
            │  └─────────────────────────────────────┘    │
            └──────────────┬───────────────────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │  Analytics & Reporting      │
            │                             │
            │ • ML Predictions            │
            │ • Risk Assessments          │
            │ • Trend Analysis            │
            │ • Dashboard Queries         │
            └─────────────────────────────┘
```

## Data Flow

```
OpenWeather API                WHO GHO API                 AWS Athena
     ↓                              ↓                           ↓
  Weather Data              Health Indicators          Disease Case Data
  (temp, humidity,          (sanitation, nutrition,    (cases, deaths,
   rainfall, wind)           healthcare access)         fatality rates)
     ↓                              ↓                           ↓
     └──────────────┬───────────────┴───────────────────────────┘
                    │
          Data Pipeline Orchestrator
          (data_pipeline.py)
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Validate  Transform  Enrich
        (Parse) (Format)  (Calculate)
          ▼         ▼         ▼
          └─────────┼─────────┘
                    │
         PostgreSQL Database
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Store    Update    Archive
       (New)    (Existing) (Old)
          ▼         ▼         ▼
          └─────────┼─────────┘
                    │
       ML Models & Analytics
          (Predictions)
                    │
            ┌───────┴───────┐
            ▼               ▼
        Alerts         Dashboard
```

## Setup Timeline

```
Step 1: Environment Setup
  Python ✓ Installed
  Packages ✓ Installed
  Configuration ✓ Created
  │
  └─→ Status: COMPLETE

Step 2: Install PostgreSQL
  Download from postgresql.org
  Run installer
  Remember password
  │
  └─→ Status: PENDING (User action required)

Step 3: Create Database
  Run: psql -U postgres -f database_schema.sql
  Creates 8 tables
  Creates 2 views
  Creates indexes
  │
  └─→ Status: PENDING

Step 4: Initialize Data (Optional)
  Run: python init_sample_data.py
  Adds sample districts
  Adds sample diseases
  │
  └─→ Status: PENDING

Step 5: Configure APIs
  Edit .env file
  Add OpenWeather API key
  Add AWS credentials
  │
  └─→ Status: PENDING

Step 6: Run Pipeline
  Run: python data_pipeline.py
  Fetches weather data
  Fetches health indicators
  Syncs disease cases
  │
  └─→ Status: PENDING

Step 7: Verify Data
  Query database
  Check logs
  Review results
  │
  └─→ Status: PENDING
```

## Module Dependencies

```
data_pipeline.py
├── db_config.py
├── openweather_api.py
│   ├── requests
│   └── db_config.py
├── gho_api.py
│   ├── requests
│   └── db_config.py
└── athena_api.py
    ├── boto3
    └── db_config.py

db_config.py
├── psycopg2
├── dotenv
└── logging

Helper Scripts
├── setup_and_demo.py (Verification)
├── init_sample_data.py (Sample data)
└── performance.py (ML evaluation)
```

## Database Schema (Simplified)

```
districts
─────────
id ──┬──────────→ weather_data
name│            id, district_id, date
lat ├──────────→ disease_cases
lon│            id, district_id, disease_id
pop└──────────→ health_indicators
                  id, district_id, disease_id
               predictions
                  id, district_id, disease_id

diseases
────────
id ──┬──────────→ disease_cases
name│            id, district_id, disease_id
code└──────────→ health_indicators
                  id, district_id, disease_id

disease_cases
──────────────
district_id ──────→ districts
disease_id ───────→ diseases
date, cases, deaths, statistics

weather_data
────────────
district_id ──────→ districts
temperature, humidity, rainfall, etc.

health_indicators
──────────────────
district_id ──────→ districts
disease_id ───────→ diseases
indicator_name, value, unit

predictions
───────────
district_id ──────→ districts
disease_id ───────→ diseases
predicted_cases, outbreak_probability
```

## API Integration Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENWEATHER API                          │
├─────────────────────────────────────────────────────────────┤
│ Free Tier:  60 requests/min, 1000 requests/day              │
│ Endpoint:   https://api.openweathermap.org/data/2.5/weather │
│ Methods:    • get_current_weather(lat, lon)                 │
│             • fetch_and_store_weather(districts)            │
│ Data:       • Temperature, Humidity, Rainfall               │
│             • Wind Speed, Pressure, Cloud Coverage          │
│ Update:     Every 6 hours (configurable)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          WHO GLOBAL HEALTH OBSERVATORY (GHO)                │
├─────────────────────────────────────────────────────────────┤
│ Free:       No authentication required                       │
│ Endpoint:   https://www.who.int/data/gho/api                │
│ Methods:    • get_country_health_profile(country_code)      │
│             • fetch_health_risk_factors(country_code)       │
│             • get_indicator_data(indicator_code)            │
│ Data:       • Health Indicators, Risk Factors               │
│             • Sanitation, Nutrition, Healthcare Access      │
│ Update:     Every 12 hours (configurable)                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              AWS ATHENA (S3 Query)                           │
├─────────────────────────────────────────────────────────────┤
│ Cost:       $5 per TB scanned                                │
│ Method:     SQL queries on S3 data                           │
│ Methods:    • execute_query(sql)                            │
│             • fetch_disease_cases(date_range)               │
│             • sync_disease_cases_to_postgresql()            │
│             • get_outbreak_alerts(threshold)                │
│ Data:       • Disease Cases, Deaths, Statistics             │
│             • Case Fatality Rates, Trends                   │
│ Update:     Every 12 hours (configurable)                   │
└─────────────────────────────────────────────────────────────┘
```

## Scheduling Overview

```
24-Hour Cycle:

00:00 ── Weather Data (every 6h)
02:00 ── Full Pipeline
04:00 ── Weather Data
08:00 ── Weather Data
12:00 ── Disease Cases Sync, Outbreak Risk Assessment
16:00 ── Weather Data
20:00 ── Disease Cases Sync, Outbreak Risk Assessment
         │
         └─→ Logs saved to data_pipeline.log
         └─→ Status recorded in api_logs table
         └─→ Sync details in data_sync_logs table
```

## Quick Reference

```
╔════════════════════════════════════════════════════════════╗
║           COMMAND REFERENCE                               ║
╠════════════════════════════════════════════════════════════╣
║ Install PostgreSQL:                                        ║
║   https://www.postgresql.org/download/windows/             ║
║                                                            ║
║ Create Database:                                           ║
║   psql -U postgres -f database_schema.sql                  ║
║                                                            ║
║ Initialize Sample Data:                                    ║
║   python init_sample_data.py                               ║
║                                                            ║
║ Run Pipeline Once:                                         ║
║   python data_pipeline.py                                  ║
║                                                            ║
║ Query Database:                                            ║
║   psql -U postgres -d pakpulse_db                          ║
║   SELECT * FROM v_current_disease_status;                 ║
║                                                            ║
║ Check Logs:                                                ║
║   tail -f data_pipeline.log                                ║
║                                                            ║
║ Monitor APIs:                                              ║
║   psql -U postgres -d pakpulse_db                          ║
║   SELECT * FROM api_logs ORDER BY created_at DESC;        ║
╚════════════════════════════════════════════════════════════╝
```

## Success Indicators

✅ **Setup Complete When:**
- All Python packages installed
- .env file created
- Database schema available
- All 5 API modules present
- Documentation complete
- Setup script runs without errors

✅ **Database Ready When:**
- PostgreSQL installed and running
- `pakpulse_db` database created
- All 8 tables created
- Sample data loaded
- Indexes created

✅ **Pipeline Running When:**
- Weather data fetched successfully
- GHO data retrieved
- Athena queries execute
- Data stored in database
- No errors in logs
- Alerts generated

---

*Visual Guide - January 27, 2026*
