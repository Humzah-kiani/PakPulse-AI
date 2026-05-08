import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration from environment variables"""
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'pakpulse_db')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'postgres')
        self.min_connections = int(os.getenv('DB_MIN_CONN', '2'))
        self.max_connections = int(os.getenv('DB_MAX_CONN', '10'))

    def get_connection_string(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseConnection:
    """PostgreSQL connection pool manager"""
    
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            config = DatabaseConfig()
            try:
                self._pool = psycopg2.pool.SimpleConnectionPool(
                    config.min_connections,
                    config.max_connections,
                    host=config.host,
                    port=config.port,
                    database=config.database,
                    user=config.user,
                    password=config.password
                )
                logger.info("Database connection pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to create connection pool: {e}")
                raise

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self._pool.putconn(conn)

    def close_all_connections(self):
        """Close all connections in the pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")

    # =====================================================
    # DISTRICTS OPERATIONS
    # =====================================================

    def insert_district(self, district_name: str, district_enc: int, 
                       latitude: float, longitude: float, population: int,
                       population_density: float, sanitation_index: float) -> int:
        """Insert a new district"""
        query = """
            INSERT INTO districts (district_name, district_enc, latitude, longitude, 
                                 population, population_density, sanitation_index)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (district_name) DO UPDATE SET 
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                population = EXCLUDED.population,
                population_density = EXCLUDED.population_density,
                sanitation_index = EXCLUDED.sanitation_index
            RETURNING district_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (district_name, district_enc, latitude, longitude,
                                  population, population_density, sanitation_index))
            district_id = cursor.fetchone()[0]
            conn.commit()
            return district_id

    def get_district_by_name(self, district_name: str) -> Optional[Dict]:
        """Get district by name"""
        query = "SELECT * FROM districts WHERE district_name = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (district_name,))
            return cursor.fetchone()

    def get_all_districts(self) -> List[Dict]:
        """Get all districts"""
        query = "SELECT * FROM districts ORDER BY district_name"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            return cursor.fetchall()

    # =====================================================
    # DISEASES OPERATIONS
    # =====================================================

    def insert_disease(self, disease_name: str, disease_enc: int, 
                      disease_code: str = None, is_outbreak_disease: bool = False) -> int:
        """Insert a new disease"""
        query = """
            INSERT INTO diseases (disease_name, disease_enc, disease_code, is_outbreak_disease)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (disease_name) DO UPDATE SET 
                disease_enc = EXCLUDED.disease_enc,
                disease_code = EXCLUDED.disease_code,
                is_outbreak_disease = EXCLUDED.is_outbreak_disease
            RETURNING disease_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (disease_name, disease_enc, disease_code, is_outbreak_disease))
            disease_id = cursor.fetchone()[0]
            conn.commit()
            return disease_id

    def get_disease_by_name(self, disease_name: str) -> Optional[Dict]:
        """Get disease by name"""
        query = "SELECT * FROM diseases WHERE disease_name = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (disease_name,))
            return cursor.fetchone()

    def get_all_diseases(self) -> List[Dict]:
        """Get all diseases"""
        query = "SELECT * FROM diseases ORDER BY disease_name"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            return cursor.fetchall()

    # =====================================================
    # WEATHER DATA OPERATIONS
    # =====================================================

    def insert_weather_data(self, district_id: int, date, temperature: float,
                           humidity: float, rainfall: float, temperature_anom: float = None,
                           humidity_anom: float = None, rainfall_anom: float = None,
                           wind_speed: float = None, pressure: float = None,
                           cloud_coverage: int = None, uv_index: float = None) -> int:
        """Insert weather data"""
        query = """
            INSERT INTO weather_data (district_id, date, temperature, humidity, rainfall,
                                     temperature_anom, humidity_anom, rainfall_anom,
                                     wind_speed, pressure, cloud_coverage, uv_index)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (district_id, date) DO UPDATE SET 
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                rainfall = EXCLUDED.rainfall,
                temperature_anom = EXCLUDED.temperature_anom,
                humidity_anom = EXCLUDED.humidity_anom,
                rainfall_anom = EXCLUDED.rainfall_anom,
                wind_speed = EXCLUDED.wind_speed,
                pressure = EXCLUDED.pressure,
                cloud_coverage = EXCLUDED.cloud_coverage,
                uv_index = EXCLUDED.uv_index,
                last_updated = CURRENT_TIMESTAMP
            RETURNING weather_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (district_id, date, temperature, humidity, rainfall,
                                  temperature_anom, humidity_anom, rainfall_anom,
                                  wind_speed, pressure, cloud_coverage, uv_index))
            weather_id = cursor.fetchone()[0]
            conn.commit()
            return weather_id

    def get_weather_by_district_date(self, district_id: int, date) -> Optional[Dict]:
        """Get weather data for a specific district and date"""
        query = "SELECT * FROM weather_data WHERE district_id = %s AND date = %s"
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (district_id, date))
            return cursor.fetchone()

    # =====================================================
    # DISEASE CASES OPERATIONS
    # =====================================================

    def insert_disease_cases(self, district_id: int, disease_id: int, date,
                            cases: int = 0, cumulative_cases: int = None,
                            deaths: int = None, case_fatality_rate: float = None,
                            lag_1: int = None, lag_2: int = None, lag_3: int = None,
                            cases_roll_mean_3: float = None, cases_roll_mean_7: float = None,
                            cases_roll_mean_14: float = None, cases_roll_std_3: float = None,
                            cases_roll_std_7: float = None, cases_roll_std_14: float = None,
                            cases_roll_sum_3: int = None, cases_roll_sum_7: int = None,
                            cases_roll_sum_14: int = None, cases_pct_change_3: float = None,
                            cases_last_1yr: int = None) -> int:
        """Insert disease case data"""
        query = """
            INSERT INTO disease_cases (district_id, disease_id, date, cases, cumulative_cases,
                                      deaths, case_fatality_rate, lag_1, lag_2, lag_3,
                                      cases_roll_mean_3, cases_roll_mean_7, cases_roll_mean_14,
                                      cases_roll_std_3, cases_roll_std_7, cases_roll_std_14,
                                      cases_roll_sum_3, cases_roll_sum_7, cases_roll_sum_14,
                                      cases_pct_change_3, cases_last_1yr)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (district_id, disease_id, date) DO UPDATE SET 
                cases = EXCLUDED.cases,
                cumulative_cases = EXCLUDED.cumulative_cases,
                deaths = EXCLUDED.deaths,
                case_fatality_rate = EXCLUDED.case_fatality_rate,
                lag_1 = EXCLUDED.lag_1,
                lag_2 = EXCLUDED.lag_2,
                lag_3 = EXCLUDED.lag_3,
                cases_roll_mean_3 = EXCLUDED.cases_roll_mean_3,
                cases_roll_mean_7 = EXCLUDED.cases_roll_mean_7,
                cases_roll_mean_14 = EXCLUDED.cases_roll_mean_14,
                cases_roll_std_3 = EXCLUDED.cases_roll_std_3,
                cases_roll_std_7 = EXCLUDED.cases_roll_std_7,
                cases_roll_std_14 = EXCLUDED.cases_roll_std_14,
                cases_roll_sum_3 = EXCLUDED.cases_roll_sum_3,
                cases_roll_sum_7 = EXCLUDED.cases_roll_sum_7,
                cases_roll_sum_14 = EXCLUDED.cases_roll_sum_14,
                cases_pct_change_3 = EXCLUDED.cases_pct_change_3,
                cases_last_1yr = EXCLUDED.cases_last_1yr,
                last_updated = CURRENT_TIMESTAMP
            RETURNING case_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (district_id, disease_id, date, cases, cumulative_cases,
                                  deaths, case_fatality_rate, lag_1, lag_2, lag_3,
                                  cases_roll_mean_3, cases_roll_mean_7, cases_roll_mean_14,
                                  cases_roll_std_3, cases_roll_std_7, cases_roll_std_14,
                                  cases_roll_sum_3, cases_roll_sum_7, cases_roll_sum_14,
                                  cases_pct_change_3, cases_last_1yr))
            case_id = cursor.fetchone()[0]
            conn.commit()
            return case_id

    def get_disease_cases_by_district_date_range(self, district_id: int, 
                                                 start_date, end_date) -> List[Dict]:
        """Get disease cases for a district in a date range"""
        query = """
            SELECT dc.*, d.disease_name, dis.district_name
            FROM disease_cases dc
            JOIN diseases d ON dc.disease_id = d.disease_id
            JOIN districts dis ON dc.district_id = dis.district_id
            WHERE dc.district_id = %s AND dc.date BETWEEN %s AND %s
            ORDER BY dc.date DESC, d.disease_name
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (district_id, start_date, end_date))
            return cursor.fetchall()

    # =====================================================
    # HEALTH INDICATORS OPERATIONS
    # =====================================================

    def insert_health_indicator(self, year: int, indicator_name: str,
                               indicator_code: str, value: float, unit: str,
                               data_source: str, district_id: int = None,
                               disease_id: int = None) -> int:
        """Insert health indicator"""
        query = """
            INSERT INTO health_indicators (district_id, disease_id, year, indicator_name,
                                          indicator_code, value, unit, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (district_id, disease_id, year, indicator_code) DO UPDATE SET
                value = EXCLUDED.value,
                data_source = EXCLUDED.data_source,
                last_updated = CURRENT_TIMESTAMP
            RETURNING indicator_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (district_id, disease_id, year, indicator_name,
                                  indicator_code, value, unit, data_source))
            indicator_id = cursor.fetchone()[0]
            conn.commit()
            return indicator_id

    # =====================================================
    # PREDICTIONS OPERATIONS
    # =====================================================

    def insert_prediction(self, district_id: int, disease_id: int, prediction_date,
                         predicted_cases: int, predicted_outbreak_probability: float,
                         confidence_score: float, model_version: str) -> int:
        """Insert prediction"""
        query = """
            INSERT INTO predictions (district_id, disease_id, prediction_date,
                                    predicted_cases, predicted_outbreak_probability,
                                    confidence_score, model_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING prediction_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (district_id, disease_id, prediction_date,
                                  predicted_cases, predicted_outbreak_probability,
                                  confidence_score, model_version))
            prediction_id = cursor.fetchone()[0]
            conn.commit()
            return prediction_id

    # =====================================================
    # LOGGING OPERATIONS
    # =====================================================

    def log_api_call(self, api_name: str, endpoint: str, status_code: int,
                    response_time_ms: int, records_fetched: int, error_message: str = None) -> int:
        """Log API call"""
        query = """
            INSERT INTO api_logs (api_name, endpoint, status_code, request_timestamp,
                                response_time_ms, records_fetched, error_message)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
            RETURNING log_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (api_name, endpoint, status_code, response_time_ms,
                                  records_fetched, error_message))
            log_id = cursor.fetchone()[0]
            conn.commit()
            return log_id

    def log_sync(self, table_name: str, records_inserted: int, records_updated: int,
                sync_start_time, sync_end_time, status: str, error_details: str = None) -> int:
        """Log data sync"""
        query = """
            INSERT INTO data_sync_logs (table_name, records_inserted, records_updated,
                                       sync_start_time, sync_end_time, status, error_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING sync_id;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (table_name, records_inserted, records_updated,
                                  sync_start_time, sync_end_time, status, error_details))
            sync_id = cursor.fetchone()[0]
            conn.commit()
            return sync_id

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    def bulk_insert_weather_data(self, records: List[tuple]) -> int:
        """Bulk insert weather data"""
        query = """
            INSERT INTO weather_data (district_id, date, temperature, humidity, rainfall,
                                     temperature_anom, humidity_anom, rainfall_anom,
                                     wind_speed, pressure, cloud_coverage, uv_index)
            VALUES %s
            ON CONFLICT (district_id, date) DO UPDATE SET
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                rainfall = EXCLUDED.rainfall,
                last_updated = CURRENT_TIMESTAMP
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted = execute_values(cursor, query, records, page_size=1000)
            conn.commit()
            return inserted

    def bulk_insert_disease_cases(self, records: List[tuple]) -> int:
        """Bulk insert disease cases"""
        query = """
            INSERT INTO disease_cases (district_id, disease_id, date, cases, cumulative_cases,
                                      deaths, case_fatality_rate, lag_1, lag_2, lag_3,
                                      cases_roll_mean_3, cases_roll_mean_7, cases_roll_mean_14,
                                      cases_roll_std_3, cases_roll_std_7, cases_roll_std_14,
                                      cases_roll_sum_3, cases_roll_sum_7, cases_roll_sum_14,
                                      cases_pct_change_3, cases_last_1yr)
            VALUES %s
            ON CONFLICT (district_id, disease_id, date) DO UPDATE SET
                cases = EXCLUDED.cases,
                cumulative_cases = EXCLUDED.cumulative_cases,
                deaths = EXCLUDED.deaths,
                last_updated = CURRENT_TIMESTAMP
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            inserted = execute_values(cursor, query, records, page_size=1000)
            conn.commit()
            return inserted
