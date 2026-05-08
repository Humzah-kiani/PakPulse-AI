#!/usr/bin/env python3
"""
Create missing api_logs table in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from db_config import DatabaseConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_api_logs_table():
    """Create the api_logs table if it doesn't exist"""
    db = DatabaseConnection()

    create_table_query = """
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
    """

    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(request_timestamp);
    """

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Create table
            cursor.execute(create_table_query)
            logger.info("api_logs table created successfully")

            # Create index
            cursor.execute(create_index_query)
            logger.info("Index on api_logs created successfully")

            conn.commit()
            logger.info("Database schema update completed successfully")

    except Exception as e:
        logger.error(f"Failed to create api_logs table: {e}")
        raise

if __name__ == "__main__":
    create_api_logs_table()