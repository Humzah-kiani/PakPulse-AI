# PakPulse Environment Configuration Template
# Copy this to .env in your project root and fill in your credentials

# ================================================
# DATABASE CONFIGURATION
# ================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pakpulse_db
DB_USER=pakpulse_user
DB_PASSWORD=your_secure_password_here

# ================================================
# OPENWEATHER API
# ================================================
# Sign up at: https://openweathermap.org/api
# Free tier: 60 calls/minute, 1M calls/month
OPENWEATHER_API_KEY=your_openweather_api_key_here

# ================================================
# WHO GHO API
# ================================================
# No API key required - publicly accessible
# https://www.who.int/data/gho/api
GHO_API_TIMEOUT=10  # Seconds

# ================================================
# AWS ATHENA CONFIGURATION
# ================================================
# AWS Credentials (from IAM console)
# Required permissions: athena:*, s3:GetObject, s3:ListBucket, s3:PutObject
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# S3 bucket for Athena query results
# Create bucket: https://s3.console.aws.amazon.com/
ATHENA_S3_OUTPUT_LOCATION=s3://pakpulse-athena-results/

# Athena database and table names
ATHENA_DATABASE=pakpulse_data
ATHENA_TABLE=disease_data

# ================================================
# DATA PIPELINE CONFIGURATION
# ================================================
# How often to fetch data (in hours)
WEATHER_FETCH_INTERVAL=1
HEALTH_INDICATORS_FETCH_INTERVAL=24
ATHENA_SYNC_INTERVAL=168  # Weekly

# ================================================
# LOGGING CONFIGURATION
# ================================================
LOG_LEVEL=INFO
LOG_FILE=data_pipeline.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5

# ================================================
# FEATURE FLAGS
# ================================================
# Set to false to disable API integration and use sample data
ENABLE_OPENWEATHER_API=true
ENABLE_GHO_API=true
ENABLE_ATHENA_API=false  # Only if AWS setup is complete

# ================================================
# MODEL CONFIGURATION
# ================================================
MODEL_TYPE=lightgbm
PREDICTION_HORIZON_DAYS=7  # Predict 7 days ahead
OUTBREAK_THRESHOLD=0.7  # Probability threshold for outbreak alert

# ================================================
# NOTIFICATION CONFIGURATION
# ================================================
ENABLE_ALERTS=false
ALERT_EMAIL=your_email@example.com
ALERT_OUTBREAK_PROBABILITY=0.8  # Alert if probability exceeds 80%
