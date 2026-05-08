-- PostgreSQL Database Schema for Disease Prediction System
-- Create database
CREATE DATABASE pakpulse_db;

-- Connect to the new database
\c pakpulse_db;

-- =====================================================
-- TABLES FOR CORE DATA
-- =====================================================

-- Districts table
CREATE TABLE IF NOT EXISTS districts (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(100) UNIQUE NOT NULL,
    district_enc INT,
    latitude FLOAT,
    longitude FLOAT,
    population INT,
    population_density FLOAT,
    sanitation_index FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Diseases table
CREATE TABLE IF NOT EXISTS diseases (
    disease_id SERIAL PRIMARY KEY,
    disease_name VARCHAR(100) UNIQUE NOT NULL,
    disease_enc INT,
    disease_code VARCHAR(50),
    description TEXT,
    is_outbreak_disease BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- WEATHER DATA (OpenWeather API)
-- =====================================================

CREATE TABLE IF NOT EXISTS weather_data (
    weather_id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    temperature FLOAT,
    temperature_anom FLOAT,
    humidity FLOAT,
    humidity_anom FLOAT,
    rainfall FLOAT,
    rainfall_anom FLOAT,
    wind_speed FLOAT,
    pressure FLOAT,
    cloud_coverage INT,
    uv_index FLOAT,
    api_source VARCHAR(50) DEFAULT 'OpenWeather',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_id, date)
);

-- =====================================================
-- DISEASE CASES DATA (Athena)
-- =====================================================

CREATE TABLE IF NOT EXISTS disease_cases (
    case_id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    disease_id INT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    cases INT DEFAULT 0,
    cumulative_cases INT,
    deaths INT DEFAULT 0,
    case_fatality_rate FLOAT,
    lag_1 INT,
    lag_2 INT,
    lag_3 INT,
    cases_roll_mean_3 FLOAT,
    cases_roll_mean_7 FLOAT,
    cases_roll_mean_14 FLOAT,
    cases_roll_std_3 FLOAT,
    cases_roll_std_7 FLOAT,
    cases_roll_std_14 FLOAT,
    cases_roll_sum_3 INT,
    cases_roll_sum_7 INT,
    cases_roll_sum_14 INT,
    cases_pct_change_3 FLOAT,
    cases_last_1yr INT,
    api_source VARCHAR(50) DEFAULT 'Athena',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_id, disease_id, date)
);

-- =====================================================
-- HEALTH OBSERVATORY DATA (GHO API)
-- =====================================================

CREATE TABLE IF NOT EXISTS health_indicators (
    indicator_id SERIAL PRIMARY KEY,
    district_id INT REFERENCES districts(district_id) ON DELETE CASCADE,
    disease_id INT REFERENCES diseases(disease_id) ON DELETE CASCADE,
    year INT,
    indicator_name VARCHAR(200),
    indicator_code VARCHAR(50),
    value FLOAT,
    unit VARCHAR(50),
    data_source VARCHAR(100),
    api_source VARCHAR(50) DEFAULT 'GHO',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_id, disease_id, year, indicator_code)
);

-- =====================================================
-- PREDICTIONS
-- =====================================================

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    disease_id INT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL,
    predicted_cases INT,
    predicted_outbreak_probability FLOAT,
    confidence_score FLOAT,
    model_version VARCHAR(50),
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- API LOGS & MONITORING
-- =====================================================

CREATE TABLE IF NOT EXISTS api_logs (
    log_id SERIAL PRIMARY KEY,
    api_name VARCHAR(50),
    endpoint VARCHAR(255),
    status_code INT,
    request_timestamp TIMESTAMP,
    response_time_ms INT,
    records_fetched INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_sync_logs (
    sync_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    records_inserted INT,
    records_updated INT,
    sync_start_time TIMESTAMP,
    sync_end_time TIMESTAMP,
    status VARCHAR(50),
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_weather_district_date ON weather_data(district_id, date);
CREATE INDEX idx_disease_cases_district_disease_date ON disease_cases(district_id, disease_id, date);
CREATE INDEX idx_health_indicators_district_disease ON health_indicators(district_id, disease_id);
CREATE INDEX idx_predictions_district_disease_date ON predictions(district_id, disease_id, prediction_date);
CREATE INDEX idx_api_logs_timestamp ON api_logs(request_timestamp);
CREATE INDEX idx_sync_logs_timestamp ON data_sync_logs(created_at);

-- =====================================================
-- VIEWS FOR EASY QUERYING
-- =====================================================

-- Current disease status
CREATE VIEW v_current_disease_status AS
SELECT 
    d.district_name,
    dis.disease_name,
    dc.date,
    dc.cases,
    wd.temperature,
    wd.humidity,
    wd.rainfall,
    p.predicted_cases,
    p.predicted_outbreak_probability
FROM disease_cases dc
JOIN districts d ON dc.district_id = d.district_id
JOIN diseases dis ON dc.disease_id = dis.disease_id
LEFT JOIN weather_data wd ON dc.district_id = wd.district_id AND dc.date = wd.date
LEFT JOIN predictions p ON dc.district_id = p.district_id 
    AND dc.disease_id = p.disease_id 
    AND dc.date = p.prediction_date
ORDER BY dc.date DESC, d.district_name, dis.disease_name;

-- Outbreak risk assessment
CREATE VIEW v_outbreak_risk AS
SELECT 
    d.district_name,
    dis.disease_name,
    dc.date,
    dc.cases,
    dc.cases_roll_mean_7,
    CASE 
        WHEN p.predicted_outbreak_probability > 0.7 THEN 'HIGH'
        WHEN p.predicted_outbreak_probability > 0.4 THEN 'MEDIUM'
        ELSE 'LOW'
    END as outbreak_risk,
    p.predicted_outbreak_probability,
    p.confidence_score
FROM disease_cases dc
JOIN districts d ON dc.district_id = d.district_id
JOIN diseases dis ON dc.disease_id = dis.disease_id
LEFT JOIN predictions p ON dc.district_id = p.district_id 
    AND dc.disease_id = p.disease_id 
    AND dc.date = p.prediction_date
WHERE dc.date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY p.predicted_outbreak_probability DESC;
