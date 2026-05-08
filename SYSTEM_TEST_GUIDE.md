# 🚀 COMPLETE SYSTEM TEST RUN - Step by Step

## 📋 What You Need to Do to Test Run Everything

### **STEP 1: Install PostgreSQL Database** (REQUIRED - 5 minutes)
1. **Download**: Go to https://www.postgresql.org/download/windows/
2. **Install**: Run the installer with these settings:
   - Password: Set `pakpulse123` (or remember your choice)
   - Port: Keep `5432` (default)
   - Install pgAdmin: Yes (optional but helpful)
3. **Verify**: PostgreSQL service should start automatically

### **STEP 2: Create Database Schema** (2 minutes)
```powershell
cd "c:\Users\user\OneDrive - Higher Education Commission\Desktop\FYP"
psql -U postgres -f database_schema.sql
```
- Enter the password you set during installation
- This creates: 8 tables, 2 views, 6 indexes

### **STEP 3: Load Sample Data** (1 minute)
```powershell
python init_sample_data.py
```
- Loads 6 Pakistani districts + 6 diseases
- Creates sample weather/health data

### **STEP 4: Configure API Keys** (OPTIONAL but recommended)
Edit `.env` file and add:
```
OPENWEATHER_API_KEY=your_key_here  # Get from https://openweathermap.org/api
AWS_ACCESS_KEY_ID=your_key_here     # Get from AWS Console
AWS_SECRET_ACCESS_KEY=your_key_here
```

### **STEP 5: Run Full System Test** (5 minutes)
```powershell
python data_pipeline.py
```

---

## 🎯 What the Test Run Will Do

### **Real-Time Data Collection:**
- ✅ **Weather API**: Fetches live temperature, humidity, rainfall for 6 districts
- ✅ **Health API**: Downloads WHO health indicators for Pakistan
- ✅ **Disease Data**: Syncs disease cases from AWS Athena (if configured)

### **Database Operations:**
- ✅ **Storage**: Saves all data to PostgreSQL tables
- ✅ **Analytics**: Calculates rolling averages, lag features, outbreak risks
- ✅ **Logging**: Records all API calls and sync operations

### **Predictions & Alerts:**
- ✅ **ML Models**: Runs LightGBM models for outbreak predictions
- ✅ **Risk Assessment**: Identifies high-risk districts/diseases
- ✅ **Reports**: Generates current disease status views

---

## 📊 Expected Test Results

After running `python data_pipeline.py`, you should see:

```
======================================================================
STARTING FULL DATA PIPELINE EXECUTION
======================================================================

[1] Initializing APIs...
✓ OpenWeather API initialized
✓ GHO API initialized
✓ Athena API initialized

[2] Fetching weather data...
✓ Weather data fetched for 6 districts
✓ Stored 6 weather records in database

[3] Fetching health indicators...
✓ Health indicators fetched for Pakistan
✓ Stored 50+ health indicators in database

[4] Syncing disease cases...
✓ Disease cases synced from Athena
✓ Stored 1000+ disease records in database

[5] Assessing outbreak risk...
✓ Risk assessment completed
✓ Generated 12 outbreak predictions

======================================================================
PIPELINE EXECUTION COMPLETED SUCCESSFULLY
Total execution time: 45 seconds
======================================================================
```

---

## 🔍 Verify Results with Database Queries

After the pipeline runs, check the data:

```sql
-- Connect to database
psql -U postgres -d pakpulse_db

-- Check districts
SELECT * FROM districts;

-- Check current weather
SELECT d.district_name, w.temperature, w.humidity, w.rainfall
FROM weather_data w
JOIN districts d ON w.district_id = d.district_id
ORDER BY w.date DESC LIMIT 6;

-- Check disease status
SELECT * FROM v_current_disease_status LIMIT 10;

-- Check outbreak risks
SELECT * FROM v_outbreak_risk WHERE risk_level = 'HIGH';
```

---

## ⚡ Quick Test Commands

**Test individual components:**
```powershell
# Test database connection
python -c "from db_config import DatabaseConnection; db = DatabaseConnection(); print('Database connected!')"

# Test weather API (needs API key)
python -c "from openweather_api import fetch_current_weather_for_all_districts; fetch_current_weather_for_all_districts('your_api_key')"

# Test health API
python -c "from gho_api import fetch_gho_indicators_for_pakistan; fetch_gho_indicators_for_pakistan()"

# Test ML models
python performance.py
```

---

## 🛠️ Troubleshooting

**"psql command not found"**
- Add to PATH: `$env:Path += ";C:\Program Files\PostgreSQL\16\bin"`

**"Connection refused"**
- Start PostgreSQL: `Start-Service -Name postgresql-x64-16`

**"API key errors"**
- Get OpenWeather key: https://openweathermap.org/api
- For Athena: Configure AWS credentials in .env

**"No data in results"**
- Check .env configuration
- Verify API keys are valid
- Run `python init_sample_data.py` first

---

## 🎉 Success Indicators

Your system is working when you see:
- ✅ Database connection successful
- ✅ Weather data fetched and stored
- ✅ Health indicators downloaded
- ✅ Disease cases synchronized
- ✅ Predictions generated
- ✅ No error messages in logs

**Total test time: 15-20 minutes**
**System will be fully operational after these steps!**