# 🌍 PakPulse API Integration Module

**Complete integration of three powerful external APIs into the PakPulse disease surveillance system.**

---

## 📦 What's Included

### 1. **OpenWeather API Integration**
- Real-time weather data for disease correlation
- 6+ weather parameters per location
- Automatic caching and rate limit handling
- Database logging of all API calls

**File**: `openweather_api.py` (265 lines)

### 2. **WHO Global Health Observatory (GHO) API**
- WHO health indicators and statistics
- Pakistan-specific health data
- No authentication required
- Disease and health outcome tracking

**File**: `gho_api.py` (369 lines)

### 3. **AWS Athena Integration**
- Query large disease datasets from S3
- SQL-based data querying
- Cost-effective big data analysis
- Data warehouse connectivity

**File**: `athena_api.py` (446 lines)

### 4. **Unified Data Pipeline**
- Orchestrates all API fetches
- Scheduled data collection
- Error handling and retries
- Comprehensive logging

**File**: `data_pipeline.py` (385 lines)

### 5. **Sample Data Initialization**
- Loads initial districts and diseases
- Fetches real API data during setup
- Graceful fallback to sample data
- Progress tracking

**File**: `init_sample_data.py` (442 lines)

### 6. **API Testing Suite**
- Comprehensive test coverage
- Validates all integrations
- Colored output and progress indication
- Diagnostic information

**File**: `test_api_integration.py` (380+ lines)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# PostgreSQL 12+
psql --version

# Required packages (install with pip)
pip install -r requirements_integration.txt
```

### Installation Steps

1. **Clone/Download Project**
   ```bash
   cd FYP
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements_integration.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy template
   cp ENV_TEMPLATE.md .env
   
   # Edit .env with your credentials
   nano .env  # or use your favorite editor
   ```

4. **Initialize Database**
   ```bash
   # Create tables (if not already done)
   psql -U pakpulse_user -d pakpulse_db -f database_schema.sql
   ```

5. **Test Integration**
   ```bash
   python test_api_integration.py
   ```

6. **Load Initial Data**
   ```bash
   python init_sample_data.py
   ```

7. **Start Data Pipeline**
   ```bash
   python data_pipeline.py
   ```

---

## 🔧 Configuration

### Required Environment Variables

```env
# Database (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pakpulse_db
DB_USER=pakpulse_user
DB_PASSWORD=secure_password

# OpenWeather API
OPENWEATHER_API_KEY=sk_xxxxxxxxxxxxx

# AWS Athena (optional)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG...
AWS_REGION=us-east-1
ATHENA_S3_OUTPUT_LOCATION=s3://bucket/athena-results/
```

### Optional Configuration

```env
# API call intervals
WEATHER_FETCH_INTERVAL=1           # hours
HEALTH_INDICATORS_FETCH_INTERVAL=24  # hours
ATHENA_SYNC_INTERVAL=168           # hours (weekly)

# Logging
LOG_LEVEL=INFO
LOG_FILE=data_pipeline.log

# Feature flags
ENABLE_OPENWEATHER_API=true
ENABLE_GHO_API=true
ENABLE_ATHENA_API=false
```

---

## 📊 API Details

### OpenWeather API
| Parameter | Details |
|-----------|---------|
| **Endpoint** | https://api.openweathermap.org |
| **Auth** | API Key |
| **Rate Limit** | 60 calls/minute, 1M/month (free) |
| **Cost** | Free |
| **Data** | Temperature, humidity, rainfall, wind, pressure |

### WHO GHO API
| Parameter | Details |
|-----------|---------|
| **Endpoint** | https://www.who.int/data/gho/api |
| **Auth** | None (public) |
| **Rate Limit** | No explicit limit |
| **Cost** | Free |
| **Data** | Health indicators, vaccination, sanitation, mortality |

### AWS Athena
| Parameter | Details |
|-----------|---------|
| **Endpoint** | AWS Console |
| **Auth** | IAM Credentials |
| **Rate Limit** | Based on subscription |
| **Cost** | $5 per TB scanned (~$0.50-5/month) |
| **Data** | Custom S3 datasets |

---

## 📁 File Structure

```
FYP/
├── openweather_api.py           # Weather data integration
├── gho_api.py                   # WHO health indicators
├── athena_api.py                # AWS Athena integration
├── data_pipeline.py             # Unified orchestrator
├── init_sample_data.py          # Data initialization (UPDATED)
├── test_api_integration.py      # Test suite (NEW)
├── API_INTEGRATION_GUIDE.md     # Detailed guide (NEW)
├── API_QUICK_START.md           # Quick reference (NEW)
├── API_INTEGRATION_README.md    # This file
├── ENV_TEMPLATE.md              # Configuration template (NEW)
├── requirements_integration.txt # Dependencies
└── database_schema.sql          # Database tables
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
python test_api_integration.py
```

Output:
```
============================================================
                  PakPulse API Integration Test Suite
============================================================

Environment Variables Configuration
  ✓ DB_HOST = localhost
  ✓ OPENWEATHER_API_KEY = sk_xxx...xxxx
  ✓ AWS_ACCESS_KEY_ID = AKIA...XXXX
  
Database Connection Test
  ✓ Connected to PostgreSQL: PostgreSQL 12.4
  ✓ districts table exists
  ✓ diseases table exists
  
OpenWeather API Test
  ✓ OpenWeatherIntegration class initialized
  ✓ OpenWeather API call successful
    • temperature: 28.5°C
    • humidity: 65%
    • rainfall: 0mm
    
WHO GHO API Test
  ✓ GHOIntegration class initialized
  ✓ WHO GHO API call successful - retrieved 127 indicators
  
AWS Athena Test
  ✓ AthenaIntegration class initialized
  ✓ Region: us-east-1
  
Data Pipeline Test
  ✓ DataPipelineOrchestrator initialized
  ✓ OpenWeather API is available
  ✓ WHO GHO API is available
  ✓ AWS Athena API is available

============================================================
                    Test Summary
============================================================

Results: 6/6 tests passed

✓ All tests passed! APIs are ready to use.
============================================================
```

### Test Individual API

```python
# Test OpenWeather
from openweather_api import OpenWeatherIntegration
weather_api = OpenWeatherIntegration("your_api_key")
data = weather_api.get_current_weather(31.5497, 74.3436)
print(data)

# Test GHO
from gho_api import GHOIntegration
gho_api = GHOIntegration()
indicators = gho_api.get_indicators()
print(indicators)

# Test Data Pipeline
from data_pipeline import DataPipelineOrchestrator
pipeline = DataPipelineOrchestrator()
weather_success, weather_failed, _ = pipeline.fetch_weather_data()
print(f"Weather: {weather_success} successful, {weather_failed} failed")
```

---

## 📈 Monitoring & Logging

### View API Call Logs
```sql
-- Last 24 hours of API calls
SELECT 
    api_name,
    COUNT(*) as total_calls,
    SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
    AVG(response_time_ms) as avg_response_ms
FROM api_call_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY api_name;
```

### Monitor Real-time Data
```sql
-- Latest weather data
SELECT district_id, temperature, humidity, wind_speed, timestamp
FROM weather_data
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;

-- Latest disease data
SELECT district_id, disease_id, cases, date
FROM disease_cases
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC;
```

### Check API Health
```bash
# Watch API calls in real-time
watch -n 5 'psql -U pakpulse_user -d pakpulse_db -c "SELECT api_name, COUNT(*) as calls, MAX(timestamp) as last_call FROM api_call_logs WHERE timestamp > NOW() - INTERVAL \"1 hour\" GROUP BY api_name;"'
```

---

## 🔐 Security Best Practices

### API Keys
- ✅ Store in `.env` file (never in code)
- ✅ Never commit `.env` to version control
- ✅ Rotate keys periodically
- ✅ Use environment-specific keys (dev, test, prod)

### Database Credentials
- ✅ Use strong passwords (20+ characters)
- ✅ Limit database user permissions
- ✅ Use connection pooling
- ✅ Enable SSL connections

### AWS Security
- ✅ Create IAM user with minimal permissions
- ✅ Use temporary credentials when possible
- ✅ Enable MFA on main account
- ✅ Monitor costs with AWS Budgets

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: "API key invalid"
```
Solution:
1. Check .env file has correct key
2. Verify key hasn't expired on provider's website
3. Regenerate key if needed
4. Test with: curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
```

**Issue**: "Connection refused" to database
```
Solution:
1. Verify PostgreSQL is running: sudo service postgresql status
2. Check DB_HOST, DB_PORT, DB_NAME in .env
3. Test connection: psql -h localhost -U pakpulse_user -d pakpulse_db
4. Check firewall/security groups allow connection
```

**Issue**: "Rate limit exceeded"
```
Solution:
1. Free tier: 60 calls/minute for OpenWeather
2. Automatic exponential backoff already implemented
3. Reduce WEATHER_FETCH_INTERVAL in .env
4. Cache responses in your application
5. Consider paid tier if heavy usage
```

**Issue**: "SSL certificate error"
```
Solution:
1. Update Python certificates: /Applications/Python\ 3.x/Install\ Certificates.command
2. Or: pip install certifi
3. Or: export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

---

## 📊 Performance Metrics

### Typical Performance
- **OpenWeather API**: 200-500ms per call
- **WHO GHO API**: 1-3s per call
- **AWS Athena**: Varies by data size (typically 10-60s)
- **Database writes**: 10-50ms per record

### Optimization Tips
1. Use caching for frequently accessed data
2. Batch API requests when possible
3. Schedule heavy queries during off-peak hours
4. Use connection pooling for database
5. Monitor response times regularly

---

## 📚 Additional Resources

- **OpenWeather API Docs**: https://openweathermap.org/api
- **WHO GHO API Docs**: https://www.who.int/data/gho
- **AWS Athena Docs**: https://docs.aws.amazon.com/athena/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Dashboard**: See COMPLETE_DELIVERABLES.md

---

## 🤝 Contributing

To extend the API integration:

1. Create new API class in `{api_name}_api.py`
2. Inherit from base pattern (check `openweather_api.py`)
3. Implement required methods:
   - `_log_api_call()` - Log all API calls
   - `get_data()` - Main API method
4. Add to `data_pipeline.py` orchestrator
5. Add tests to `test_api_integration.py`
6. Update documentation

---

## 📄 License

Part of the PakPulse Disease Surveillance System (FYP Project)

---

## ✅ Checklist: API Integration

- [ ] Set up OpenWeather API account
- [ ] Add API keys to `.env`
- [ ] Install dependencies: `pip install -r requirements_integration.txt`
- [ ] Run tests: `python test_api_integration.py`
- [ ] Initialize data: `python init_sample_data.py`
- [ ] Start pipeline: `python data_pipeline.py`
- [ ] Verify data in database
- [ ] Set up monitoring queries
- [ ] Configure alerts (optional)
- [ ] Document API keys securely

---

## 🆘 Need Help?

1. Check **API_QUICK_START.md** for common tasks
2. Read **API_INTEGRATION_GUIDE.md** for detailed docs
3. Run **test_api_integration.py** to diagnose issues
4. Check logs: `tail -f data_pipeline.log`
5. Query database: `SELECT * FROM api_call_logs ORDER BY timestamp DESC LIMIT 20;`

---

**Last Updated**: March 2026  
**Version**: 2.0 (with Full API Integration)  
**Status**: ✅ Production Ready
