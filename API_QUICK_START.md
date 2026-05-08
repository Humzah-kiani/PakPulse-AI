# 🚀 PakPulse API Integration - Quick Setup Guide

## Overview
Your PakPulse system now integrates **three powerful APIs** for real-time disease surveillance data:

| API | Purpose | Status |
|-----|---------|--------|
| 🌡️ **OpenWeather** | Weather data correlation | Ready to use |
| 🏥 **WHO GHO** | Health indicators | No setup required |
| ☁️ **AWS Athena** | Large-scale data querying | Optional |

---

## ⚡ Quick Start (5 minutes)

### 1. Update Your `.env` File
Add these to your existing `.env`:

```env
# OpenWeather API (required)
OPENWEATHER_API_KEY=sk_xxxxxxxxxxxxx

# AWS (optional, for Athena)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPbgkeyEXAMPLE
AWS_REGION=us-east-1
ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket/athena-results/
```

### 2. Get OpenWeather API Key (2 minutes)
1. Go to: https://openweathermap.org/api
2. Sign up → "API keys" tab → Copy your free key
3. Paste in `.env`

### 3. Test the Integration
```bash
python test_api_integration.py
```

You should see:
```
✓ Environment Variables: PASSED
✓ Database Connection: PASSED
✓ OpenWeather API: PASSED
✓ WHO GHO API: PASSED
✓ Data Pipeline: PASSED
```

### 4. Initialize with APIs
```bash
python init_sample_data.py
```

Output:
```
PakPulse - Initializing Sample Data with API Integration
==================================================

Step 1: Inserting base districts... ✓
Step 2: Inserting diseases... ✓
Step 3: Inserting disease cases... ✓
Step 4: Inserting weather data... ✓

API INTEGRATION
==================================================

Fetching weather data from OpenWeather API...
✓ Fetched weather data: 6 successful, 0 failed

Fetching health indicators from WHO GHO API...
✓ Fetched health indicators: 10 indicators processed

✅ INITIALIZATION COMPLETE!
```

### 5. Monitor Live Data
```bash
python data_pipeline.py
```

---

## 📋 What Gets Integrated

### OpenWeather API
- **Fetches**: Temperature, humidity, rainfall, wind speed, pressure
- **For**: All 6 Pakistani districts
- **Frequency**: Every 1 hour (configurable)
- **Cost**: Free (60 calls/min, 1M calls/month)

### WHO GHO API  
- **Fetches**: Vaccination rates, sanitation access, healthcare access, mortality data
- **For**: Pakistan national-level indicators
- **Frequency**: Daily
- **Cost**: Free (no rate limits)

### AWS Athena
- **Query**: Large disease datasets from S3
- **For**: Historical analysis and machine learning
- **Frequency**: Weekly
- **Cost**: $5 per TB scanned (~$0.50-5/month)

---

## 🔍 Verify Integration

### Check Database Logs
```sql
-- View all API calls
SELECT api_name, COUNT(*) as calls, 
       SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as successful
FROM api_call_logs
GROUP BY api_name;

-- View last 24 hours
SELECT * FROM api_call_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

### Check Fetched Data
```sql
-- Latest weather data
SELECT district_id, temperature, humidity, wind_speed, timestamp
FROM weather_data
ORDER BY timestamp DESC LIMIT 6;

-- Health indicators
SELECT * FROM health_indicators LIMIT 10;
```

---

## 🚨 Troubleshooting

### "API key invalid"
→ Check OpenWeather dashboard: https://openweathermap.org/api/keys

### "Connection timeout"
→ Check internet connection and firewall settings

### "Rate limit exceeded"
→ Free tier allows 60 calls/minute (automatic backoff implemented)

### "AWS credentials invalid"
→ Regenerate keys in AWS IAM console

### "Database connection failed"
→ Ensure PostgreSQL is running and credentials are correct

---

## 📊 API Usage & Monitoring

### Real-time Monitoring
```bash
# Watch API calls in real-time
python -c "
import psycopg2
from dotenv import load_dotenv
import os
import time

load_dotenv()
conn = psycopg2.connect(
    f'postgresql://{os.getenv(\"DB_USER\")}:{os.getenv(\"DB_PASSWORD\")}@{os.getenv(\"DB_HOST\")}/{os.getenv(\"DB_NAME\")}'
)

while True:
    cur = conn.cursor()
    cur.execute('SELECT api_name, COUNT(*), AVG(response_time_ms) FROM api_call_logs WHERE timestamp > NOW() - INTERVAL \"1 hour\" GROUP BY api_name')
    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]} calls, avg {row[2]:.0f}ms')
    time.sleep(5)
    print()
"
```

### Cost Tracking (AWS Athena)
```sql
-- Estimate Athena costs
SELECT 
    SUM(bytes_scanned) / 1024 / 1024 / 1024 as gb_scanned,
    ROUND(SUM(bytes_scanned) / 1024 / 1024 / 1024 / 1024 * 5, 2) as estimated_cost_usd
FROM athena_query_logs
WHERE query_date >= CURRENT_DATE - INTERVAL '7 days';
```

---

## 📚 Documentation

- **Full API Integration Guide**: [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)
- **Environment Template**: [ENV_TEMPLATE.md](ENV_TEMPLATE.md)
- **Database Schema**: [database_schema.sql](database_schema.sql)
- **System Status**: `python system_status.py`

---

## 🎯 Next Steps

1. ✅ Set up OpenWeather API key
2. ✅ Run `test_api_integration.py` to verify
3. ✅ Run `init_sample_data.py` to fetch initial data
4. ✅ Run `data_pipeline.py` for continuous updates
5. ✅ Train models: `python Design_FYP/feature_engineer.py`
6. ✅ Make predictions: `python predict.py`

---

## 💡 Tips & Best Practices

### Optimize API Costs
- Cache responses for 1-6 hours
- Use batch requests when possible
- Schedule heavy queries during off-peak hours
- Monitor usage via `api_call_logs`

### Ensure Data Quality
- Validate API responses before storing
- Check for missing or duplicate data
- Log all errors for debugging
- Set up alerts for API failures

### Scale the System
- Use connection pooling for database
- Implement API request queuing
- Cache frequently accessed data
- Monitor response times

---

## 📞 Support

**Issues?** Check these first:
1. Is your `.env` file correctly configured?
2. Does your internet connection work?
3. Are API keys still valid?
4. Is PostgreSQL running?
5. Do database tables exist?

Run: `python test_api_integration.py` to diagnose issues.

---

## 📅 Version Info
- **PakPulse**: v2.0 (with API Integration)
- **Updated**: March 2026
- **Tested on**: Python 3.8+, PostgreSQL 12+

---

**Happy Data Integrating! 🎉**
