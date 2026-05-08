# PakPulse API Integration Guide

This guide covers integrating three external APIs into your PakPulse disease surveillance system:
1. **OpenWeather API** - Real-time weather data
2. **WHO GHO API** - Global Health Observatory indicators
3. **AWS Athena** - Large-scale disease data querying

---

## 1. OpenWeather API Integration

### Overview
Fetches current weather conditions for all Pakistani districts to correlate weather patterns with disease outbreaks.

### Setup Steps

#### Step 1: Get API Key
1. Visit [OpenWeather API](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key (free tier allows 60 calls/minute)

#### Step 2: Configure Environment
Add to your `.env` file:
```
OPENWEATHER_API_KEY=your_api_key_here
```

#### Step 3: How It Works
The `OpenWeatherIntegration` class:
- Calls current weather endpoint for each district
- Extracts: temperature, humidity, rainfall, wind speed, pressure, cloud coverage
- Stores data in `weather_data` table with timestamps
- Logs all API calls to `api_call_logs` table

#### Step 4: Usage
```python
from openweather_api import OpenWeatherIntegration

weather_api = OpenWeatherIntegration("your_api_key")
weather = weather_api.get_current_weather(latitude=31.5497, longitude=74.3436)
# Returns: {
#   'temperature': 25.5,
#   'humidity': 60,
#   'rainfall': 0,
#   'wind_speed': 5.2,
#   'pressure': 1013,
#   'cloud_coverage': 20
# }
```

#### Pricing
- **Free Tier**: 60 calls/minute, 1,000,000 calls/month ✓
- **Pro Tier**: Higher limits (paid)

---

## 2. WHO Global Health Observatory (GHO) API

### Overview
Fetches global health indicators including vaccination rates, sanitation access, malnutrition prevalence, and healthcare access statistics.

### Setup Steps

#### Step 1: API Access
No API key required! The GHO API is publicly accessible.
- Base URL: `https://www.who.int/data/gho/api`
- Documentation: [WHO GHO API Docs](https://www.who.int/data/gho)

#### Step 2: Configure Environment
No configuration needed, but you can optionally set:
```
GHO_API_TIMEOUT=10  # Request timeout in seconds
```

#### Step 3: How It Works
The `GHOIntegration` class:
- Queries available health indicators
- Retrieves Pakistan-specific data
- Extracts relevant indicators:
  - Vaccination coverage rates
  - Access to sanitation facilities
  - Healthcare service access
  - Malnutrition prevalence
  - Disease mortality rates

#### Step 4: Usage
```python
from gho_api import GHOIntegration

gho_api = GHOIntegration()

# Get list of all indicators
indicators = gho_api.get_indicators()

# Get Pakistan data for specific indicator
pakistan_data = gho_api.get_country_data('PAK', 'VACCINATION')
```

#### Key Indicators
| Indicator | Code | Use Case |
|-----------|------|----------|
| Vaccination Coverage | VACCINATION | Predict outbreak risk |
| Sanitation Access | ACCESS_SANITATION | Identify high-risk areas |
| Malnutrition | MALNUTRITION | Predict disease severity |
| Healthcare Access | HEALTHCARE_ACCESS | Assess response capacity |
| Mortality Rates | MORTALITY | Track disease severity |

---

## 3. AWS Athena Integration

### Overview
AWS Athena allows querying large datasets stored in S3 using SQL. Use this for historical disease data analysis and large-scale queries.

### Prerequisites
- AWS Account
- S3 bucket with disease data
- IAM user with Athena and S3 permissions

### Setup Steps

#### Step 1: Create AWS Account & Resources
1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Create/configure S3 bucket for data storage
3. Create IAM user with these permissions:
   - `athena:*` - Full Athena access
   - `s3:GetObject`, `s3:ListBucket` - Read from data bucket
   - `s3:PutObject` - Write query results

#### Step 2: Configure Environment
Add to `.env`:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket-name/athena-results/
```

#### Step 3: Set Up Athena Database
1. Go to AWS Athena console
2. Create database: `pakpulse_data`
3. Create table with your disease data schema
4. Upload data to S3 bucket

#### Step 4: Usage
```python
from athena_api import AthenaIntegration

athena = AthenaIntegration(
    aws_access_key_id="key",
    aws_secret_access_key="secret",
    region_name="us-east-1",
    s3_output_location="s3://bucket/results/"
)

# Execute SQL query
result = athena.execute_query("""
    SELECT district, disease, COUNT(*) as cases
    FROM disease_data
    WHERE date >= DATE '2024-01-01'
    GROUP BY district, disease
""")

print(result['results'])
```

#### Pricing
- Query scanning: $5 per TB of data scanned
- S3 storage: ~$0.023 per GB/month
- Estimate: $0.50-5/month for typical usage

---

## 4. Running API Integration

### Automated Initialization
Run all data initialization + API integration:
```bash
python init_sample_data.py
```

This will:
1. ✓ Insert 6 sample districts
2. ✓ Insert 6 sample diseases
3. ✓ Insert baseline weather data
4. ✓ Insert baseline disease cases
5. ✓ Try to fetch real OpenWeather data
6. ✓ Try to fetch WHO health indicators
7. ✓ Initialize AWS Athena (if credentials provided)

### Continuous Data Pipeline
Run the scheduled data pipeline:
```bash
python data_pipeline.py
```

This will:
- Fetch weather data every hour
- Fetch health indicators daily
- Sync Athena data weekly
- Log all API calls to database

---

## 5. API Call Logging

All API calls are logged to the `api_call_logs` table:

| Column | Purpose |
|--------|---------|
| `timestamp` | When the call was made |
| `api_name` | Which API (OpenWeather, GHO, Athena) |
| `endpoint` | Specific API endpoint |
| `status_code` | HTTP response code (200, 429, 500, etc.) |
| `response_time_ms` | How long the call took |
| `records_fetched` | Number of records returned |
| `error_message` | Error details if failed |

Query logs:
```sql
SELECT 
    DATE(timestamp) as date,
    api_name,
    COUNT(*) as calls,
    AVG(response_time_ms) as avg_response_ms,
    SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as successful
FROM api_call_logs
GROUP BY DATE(timestamp), api_name
ORDER BY date DESC;
```

---

## 6. Error Handling & Troubleshooting

### OpenWeather API Issues
```
Error: "API key invalid"
→ Check OPENWEATHER_API_KEY in .env
→ Verify key hasn't reached rate limit

Error: "401 Unauthorized"
→ API key may be deactivated
→ Generate new key from OpenWeather dashboard

Error: "429 Too Many Requests"
→ Rate limited (60 calls/minute on free tier)
→ Implement exponential backoff (already in code)
```

### GHO API Issues
```
Error: "No data available for indicator"
→ Indicator may not have Pakistan data
→ Check WHO GHO website for data availability

Error: "Connection timeout"
→ WHO servers might be slow
→ Increase timeout: GHO_API_TIMEOUT=30
```

### Athena/AWS Issues
```
Error: "InvalidCredentialsException"
→ Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
→ Verify IAM user has Athena permissions

Error: "Query execution failed"
→ Check database and table exist in Athena
→ Verify SQL syntax
→ Check S3 path permissions

Error: "The bucket does not exist"
→ Create S3 bucket in same region
→ Update ATHENA_S3_OUTPUT_LOCATION
```

---

## 7. Performance Optimization

### Reduce API Costs
1. **Cache Results**: Store API responses for 1-6 hours
2. **Batch Requests**: Combine multiple requests
3. **Selective Queries**: Only query needed districts/indicators
4. **Off-peak Hours**: Schedule heavy queries at night

### Example: Caching
```python
import time
from functools import wraps

def cache_api_response(seconds=3600):
    """Cache API responses for specified seconds"""
    def decorator(func):
        cache = {}
        last_update = {}
        
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()
            
            if key in cache and (now - last_update.get(key, 0)) < seconds:
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            last_update[key] = now
            return result
        
        return wrapper
    return decorator

@cache_api_response(seconds=3600)  # Cache for 1 hour
def get_weather_data(latitude, longitude):
    return weather_api.get_current_weather(latitude, longitude)
```

---

## 8. Monitoring & Alerts

### Database Queries for Monitoring

```sql
-- Check API health
SELECT 
    api_name,
    COUNT(*) as total_calls,
    SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
    AVG(response_time_ms) as avg_response_ms,
    MAX(timestamp) as last_call
FROM api_call_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY api_name;

-- Check for API errors
SELECT 
    api_name,
    error_message,
    COUNT(*) as occurrences,
    MAX(timestamp) as last_error
FROM api_call_logs
WHERE status_code != 200 AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY api_name, error_message
ORDER BY occurrences DESC;

-- Check rate limiting
SELECT 
    api_name,
    COUNT(*) as calls_in_minute,
    MIN(timestamp) as window_start,
    MAX(timestamp) as window_end
FROM api_call_logs
WHERE timestamp > NOW() - INTERVAL '1 minute'
GROUP BY api_name, EXTRACT(MINUTE FROM timestamp)
HAVING COUNT(*) > 50;
```

---

## 9. Integration Checklist

- [ ] Set up OpenWeather API account & get API key
- [ ] Add OPENWEATHER_API_KEY to .env
- [ ] Test OpenWeather integration: `python -c "from openweather_api import OpenWeatherIntegration"`
- [ ] Verify WHO GHO API accessibility
- [ ] Create AWS account and set up S3 bucket
- [ ] Create IAM user with required permissions
- [ ] Add AWS credentials to .env
- [ ] Create Athena database and tables
- [ ] Run: `python init_sample_data.py`
- [ ] Check database logs for API calls
- [ ] Monitor `api_call_logs` table
- [ ] Set up monitoring queries
- [ ] Configure alert thresholds

---

## 10. Next Steps

1. **Data Validation**: Review API data quality in database
2. **Feature Engineering**: Use API data to create predictive features
3. **Model Training**: Train disease outbreak prediction models
4. **Real-time Prediction**: Deploy model with live API updates
5. **Dashboard**: Visualize API data and predictions

---

## Support & Resources

- **OpenWeather**: https://openweathermap.org/api
- **WHO GHO**: https://www.who.int/data/gho
- **AWS Athena**: https://aws.amazon.com/athena/
- **Project Docs**: See COMPLETE_DELIVERABLES.md

