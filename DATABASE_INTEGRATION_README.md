# PostgreSQL + API Integration Setup Guide

## Overview
This project integrates disease prediction models with a PostgreSQL database and multiple data sources:
- **OpenWeather API**: Weather data (temperature, humidity, rainfall)
- **WHO Global Health Observatory (GHO)**: Health indicators and risk factors
- **AWS Athena**: Disease case data from S3
- **PostgreSQL**: Central data warehouse

## Architecture

```
┌─────────────────────────────────────────┐
│      Data Pipeline Orchestrator         │
│    (data_pipeline.py)                   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
    ┌──────┐┌──────┐┌──────────┐
    │GHO   ││OpenWe││ Athena   │
    │API   ││ather ││ (AWS)    │
    │      ││API   ││          │
    └──┬───┘└──┬───┘└────┬─────┘
       │       │         │
       └───────┼─────────┘
               │
               ▼
        ┌─────────────────┐
        │  PostgreSQL DB  │
        │  (pakpulse_db)  │
        └─────────────────┘
               │
               ▼
        ┌─────────────────┐
        │ ML Models &     │
        │ Predictions     │
        └─────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install psycopg2-binary python-dotenv requests schedule boto3
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
OPENWEATHER_API_KEY=your_openweather_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

### 3. Setup PostgreSQL Database

```bash
# On Windows (using psql)
psql -U postgres -f database_schema.sql

# Or on Linux/Mac
sudo -u postgres psql -f database_schema.sql
```

Or use the Python script to set up:
```python
from db_config import DatabaseConnection
db = DatabaseConnection()
# Tables will be created automatically on first connection
```

### 4. Initialize Database with District/Disease Data

```python
from db_config import DatabaseConnection

db = DatabaseConnection()

# Add districts
db.insert_district(
    district_name='Lahore',
    district_enc=0,
    latitude=31.5204,
    longitude=74.3587,
    population=11126285,
    population_density=8000,
    sanitation_index=0.75
)

# Add diseases
db.insert_disease(
    disease_name='COVID-19',
    disease_enc=0,
    disease_code='COVID-19',
    is_outbreak_disease=True
)
```

### 5. Get API Keys

#### OpenWeather API
1. Go to https://openweathermap.org/api
2. Sign up for free tier
3. Copy your API key to `.env`

#### AWS Athena
1. Set up AWS account and IAM credentials
2. Create S3 bucket for Athena query results
3. Set up Athena tables with your disease data
4. Configure credentials in `.env`

#### GHO API
- No authentication required, but respectful rate limiting recommended
- API Endpoint: https://www.who.int/data/gho/api

## File Structure

```
FYP/
├── database_schema.sql          # PostgreSQL DDL
├── db_config.py                 # Database connection & ORM
├── openweather_api.py           # OpenWeather API integration
├── gho_api.py                   # WHO GHO API integration
├── athena_api.py                # AWS Athena integration
├── data_pipeline.py             # Pipeline orchestrator
├── .env.example                 # Configuration template
├── performance.py               # ML model evaluation
└── README.md                    # This file
```

## Usage

### Running the Full Pipeline

```python
from data_pipeline import DataPipelineOrchestrator

orchestrator = DataPipelineOrchestrator()
results = orchestrator.run_full_pipeline()

print(f"Weather: {results['weather']}")
print(f"Health Indicators: {results['health_indicators']}")
print(f"Disease Cases: {results['disease_cases']}")
print(f"Outbreak Alerts: {results['outbreak_alerts']}")
```

### Running Individual Components

#### Weather Data Fetch
```python
from openweather_api import OpenWeatherIntegration

weather = OpenWeatherIntegration(api_key='your_key')
data = weather.get_current_weather(latitude=31.5204, longitude=74.3587)
print(f"Temperature: {data['temperature']}°C")
```

#### Health Indicators
```python
from gho_api import GHOIntegration

gho = GHOIntegration()
profile = gho.get_country_health_profile('PAK')
print(f"Pakistan Health Profile: {profile}")
```

#### Disease Cases Sync
```python
from athena_api import AthenaIntegration

athena = AthenaIntegration(
    aws_access_key_id='key',
    aws_secret_access_key='secret'
)

cases = athena.fetch_disease_cases()
print(f"Fetched {len(cases)} disease cases")
```

### Scheduling Automated Runs

```python
from data_pipeline import DataPipelineOrchestrator

orchestrator = DataPipelineOrchestrator()
orchestrator.run_scheduler()  # Runs continuously with scheduled jobs
```

Scheduled Jobs:
- Daily full pipeline at 2:00 AM
- Weather data fetch every 6 hours
- Disease cases sync every 12 hours
- Outbreak risk assessment every 4 hours

## Database Schema

### Main Tables

1. **districts**: District information
   - district_id, district_name, latitude, longitude
   - population, population_density, sanitation_index

2. **diseases**: Disease information
   - disease_id, disease_name, disease_code
   - is_outbreak_disease flag

3. **weather_data**: Weather information from OpenWeather
   - temperature, humidity, rainfall, wind_speed
   - pressure, cloud_coverage, uv_index

4. **disease_cases**: Case counts and statistics
   - cases, cumulative_cases, deaths
   - Lag features and rolling statistics

5. **health_indicators**: WHO GHO data
   - indicator_name, indicator_code, value
   - From WHO Global Health Observatory

6. **predictions**: Model predictions
   - predicted_cases, predicted_outbreak_probability
   - confidence_score, model_version

### Useful Views

```sql
-- Current disease status
SELECT * FROM v_current_disease_status;

-- Outbreak risk assessment
SELECT * FROM v_outbreak_risk WHERE outbreak_risk = 'HIGH';
```

## API Rate Limits

- **OpenWeather Free**: 60 requests/minute, 1000 requests/day
- **GHO**: ~100 requests/minute (recommended)
- **Athena**: Charged per TB scanned, not rate-limited

## Monitoring & Logging

Logs are written to:
- Console output
- `data_pipeline.log` file

Check logs for:
```bash
tail -f data_pipeline.log
```

API calls are logged to `api_logs` table:
```sql
SELECT * FROM api_logs ORDER BY created_at DESC LIMIT 10;
```

Data sync logs:
```sql
SELECT * FROM data_sync_logs ORDER BY created_at DESC LIMIT 10;
```

## Troubleshooting

### Database Connection Issues
```python
from db_config import DatabaseConnection
try:
    db = DatabaseConnection()
    districts = db.get_all_districts()
    print(f"Connected! Found {len(districts)} districts")
except Exception as e:
    print(f"Connection failed: {e}")
```

### API Key Issues
- Verify `.env` file exists and is in correct location
- Check credentials are correctly set
- Use `load_dotenv(verbose=True)` to debug

### Query Timeouts (Athena)
- Increase `timeout_seconds` parameter in execute_query()
- Check S3 bucket location is correct
- Verify Athena permissions

## Performance Optimization

1. **Database**: Use indexes on date, district, disease columns
2. **Batch Operations**: Use `bulk_insert_*` methods for large datasets
3. **Connection Pooling**: Automatically handled by `DatabaseConnection`
4. **Caching**: Cache district/disease lookups in memory

## Security Considerations

1. Never commit `.env` file to version control
2. Use IAM roles instead of hardcoded AWS credentials in production
3. Rotate API keys regularly
4. Use encrypted connections for database (SSL)
5. Implement API rate limiting on your endpoints

## Next Steps

1. Load your historical disease data into Athena
2. Configure AWS credentials and S3 bucket
3. Set up cron job to run `data_pipeline.py` scheduler
4. Integrate predictions into web dashboard
5. Set up alerts for high-risk areas

## Support & Documentation

- PostgreSQL: https://www.postgresql.org/docs/
- OpenWeather: https://openweathermap.org/api
- WHO GHO: https://www.who.int/data/gho
- AWS Athena: https://docs.aws.amazon.com/athena/

## License

This project is part of FYP research on disease outbreak prediction.
