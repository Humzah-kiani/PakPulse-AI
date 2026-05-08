import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import time
import pandas as pd
from db_config import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AthenaIntegration:
    """Integration with AWS Athena for querying disease data from S3"""
    
    def __init__(self, aws_access_key_id: str = None, aws_secret_access_key: str = None,
                 region_name: str = 'us-east-1', s3_output_location: str = None):
        """
        Initialize Athena integration
        
        Args:
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region_name: AWS region
            s3_output_location: S3 location for query results (s3://bucket/path/)
        """
        self.db = DatabaseConnection()
        self.s3_output_location = s3_output_location or 's3://pakpulse-athena-results/'
        
        # Initialize Athena client
        try:
            self.athena_client = boto3.client(
                'athena',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            self.s3_client = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            logger.info("Athena client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Athena client: {e}")
            raise

    def _log_api_call(self, endpoint: str, status_code: int,
                     response_time: int, records: int, error: str = None):
        """Log API call to database"""
        try:
            self.db.log_api_call('Athena', endpoint, status_code,
                               response_time, records, error)
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def execute_query(self, query: str, database: str = 'pakpulse_data',
                     timeout_seconds: int = 300) -> Optional[Dict]:
        """
        Execute an Athena query
        
        Args:
            query: SQL query to execute
            database: Athena database name
            timeout_seconds: Query timeout
            
        Returns:
            Query execution details or None
        """
        start_time = time.time()
        
        try:
            # Start query execution
            response = self.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': database},
                ResultConfiguration={'OutputLocation': self.s3_output_location}
            )
            
            query_id = response['QueryExecutionId']
            logger.info(f"Query started with ID: {query_id}")
            
            # Wait for query to complete
            query_status = self._wait_for_query(query_id, timeout_seconds)
            
            if query_status == 'SUCCEEDED':
                results = self._get_query_results(query_id)
                response_time = int((time.time() - start_time) * 1000)
                record_count = len(results) if results else 0
                
                self._log_api_call(f"Query: {query[:50]}...", 200, response_time, record_count)
                
                return {
                    'query_id': query_id,
                    'status': query_status,
                    'results': results,
                    'record_count': record_count
                }
            else:
                error_msg = f"Query failed with status: {query_status}"
                response_time = int((time.time() - start_time) * 1000)
                self._log_api_call(f"Query: {query[:50]}...", 400, response_time, 0, error_msg)
                logger.error(error_msg)
                return None
                
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            self._log_api_call(f"Query: {query[:50]}...", 0, response_time, 0, str(e))
            logger.error(f"Error executing query: {e}")
            return None

    def _wait_for_query(self, query_id: str, timeout_seconds: int = 300) -> str:
        """
        Wait for query to complete
        
        Args:
            query_id: Athena query ID
            timeout_seconds: Maximum time to wait
            
        Returns:
            Query status (SUCCEEDED, FAILED, CANCELLED)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            response = self.athena_client.get_query_execution(QueryExecutionId=query_id)
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                return status
            
            logger.info(f"Query {query_id} status: {status}")
            time.sleep(2)  # Check every 2 seconds
        
        logger.warning(f"Query {query_id} timed out after {timeout_seconds} seconds")
        return 'TIMEOUT'

    def _get_query_results(self, query_id: str) -> List[Dict]:
        """
        Get results from completed query
        
        Args:
            query_id: Athena query ID
            
        Returns:
            List of result dictionaries
        """
        try:
            results = []
            paginator = self.athena_client.get_paginator('get_query_results')
            
            for page in paginator.paginate(QueryExecutionId=query_id):
                rows = page['ResultSet']['Rows']
                
                # First row is column headers
                if not results and len(rows) > 0:
                    columns = [col['VarCharValue'] for col in rows[0]['Data']]
                
                # Process data rows
                for row in rows[1:]:
                    values = [col.get('VarCharValue', None) for col in row['Data']]
                    result_dict = dict(zip(columns, values))
                    results.append(result_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving query results: {e}")
            return []

    def fetch_disease_cases(self, start_date: datetime = None,
                           end_date: datetime = None) -> Optional[List[Dict]]:
        """
        Fetch disease cases from Athena
        
        Args:
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            List of disease case records or None
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        query = f"""
        SELECT 
            district,
            disease,
            date,
            cases,
            lag_1,
            lag_2,
            lag_3,
            cases_roll_mean_3,
            cases_roll_mean_7,
            cases_roll_mean_14,
            cases_roll_std_3,
            cases_roll_std_7,
            cases_roll_std_14
        FROM disease_cases_table
        WHERE date BETWEEN '{start_date.date()}' AND '{end_date.date()}'
        ORDER BY date DESC, district, disease
        """
        
        result = self.execute_query(query)
        return result['results'] if result else None

    def fetch_district_data(self, district_name: str) -> Optional[List[Dict]]:
        """
        Fetch all disease data for a specific district
        
        Args:
            district_name: Name of the district
            
        Returns:
            List of records or None
        """
        query = f"""
        SELECT 
            date,
            disease,
            cases,
            cases_roll_mean_7,
            cases_roll_std_7
        FROM disease_cases_table
        WHERE district = '{district_name}'
        AND date >= DATE_ADD('day', -365, CURRENT_DATE)
        ORDER BY date DESC, disease
        """
        
        result = self.execute_query(query)
        return result['results'] if result else None

    def fetch_disease_data(self, disease_name: str) -> Optional[List[Dict]]:
        """
        Fetch all data for a specific disease across districts
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            List of records or None
        """
        query = f"""
        SELECT 
            date,
            district,
            cases,
            cumulative_cases,
            deaths,
            case_fatality_rate
        FROM disease_cases_table
        WHERE disease = '{disease_name}'
        AND date >= DATE_ADD('day', -365, CURRENT_DATE)
        ORDER BY date DESC, district
        """
        
        result = self.execute_query(query)
        return result['results'] if result else None

    def get_outbreak_alerts(self, threshold_zscore: float = 2.5) -> Optional[List[Dict]]:
        """
        Get potential outbreak alerts based on Z-score threshold
        
        Args:
            threshold_zscore: Z-score threshold for alert
            
        Returns:
            List of potential outbreaks or None
        """
        query = f"""
        SELECT 
            district,
            disease,
            date,
            cases,
            cases_roll_mean_7,
            cases_roll_std_7,
            ((cases - cases_roll_mean_7) / (cases_roll_std_7 + 0.001)) as zscore
        FROM disease_cases_table
        WHERE date >= DATE_ADD('day', -30, CURRENT_DATE)
        AND ((cases - cases_roll_mean_7) / (cases_roll_std_7 + 0.001)) > {threshold_zscore}
        ORDER BY zscore DESC, date DESC
        """
        
        result = self.execute_query(query)
        return result['results'] if result else None

    def sync_disease_cases_to_postgresql(self, start_date: datetime = None,
                                        end_date: datetime = None) -> Tuple[int, int, int]:
        """
        Sync disease cases from Athena to PostgreSQL
        
        Args:
            start_date: Start date for sync
            end_date: End date for sync
            
        Returns:
            Tuple of (successfully synced, failed, total)
        """
        sync_start = datetime.now()
        successful = 0
        failed = 0
        
        try:
            # Fetch disease cases from Athena
            cases_data = self.fetch_disease_cases(start_date, end_date)
            
            if not cases_data:
                logger.warning("No disease cases found in Athena")
                return 0, 0, 0
            
            total = len(cases_data)
            
            # Process each record
            for record in cases_data:
                try:
                    # Get or create district
                    district_name = record.get('district')
                    district = self.db.get_district_by_name(district_name)
                    
                    if not district:
                        logger.warning(f"District not found: {district_name}")
                        failed += 1
                        continue
                    
                    district_id = district['district_id']
                    
                    # Get or create disease
                    disease_name = record.get('disease')
                    disease = self.db.get_disease_by_name(disease_name)
                    
                    if not disease:
                        logger.warning(f"Disease not found: {disease_name}")
                        failed += 1
                        continue
                    
                    disease_id = disease['disease_id']
                    
                    # Insert into PostgreSQL
                    self.db.insert_disease_cases(
                        district_id=district_id,
                        disease_id=disease_id,
                        date=record.get('date'),
                        cases=int(record.get('cases', 0)),
                        lag_1=int(record.get('lag_1', 0)) if record.get('lag_1') else None,
                        lag_2=int(record.get('lag_2', 0)) if record.get('lag_2') else None,
                        lag_3=int(record.get('lag_3', 0)) if record.get('lag_3') else None,
                        cases_roll_mean_3=float(record.get('cases_roll_mean_3')) if record.get('cases_roll_mean_3') else None,
                        cases_roll_mean_7=float(record.get('cases_roll_mean_7')) if record.get('cases_roll_mean_7') else None,
                        cases_roll_mean_14=float(record.get('cases_roll_mean_14')) if record.get('cases_roll_mean_14') else None,
                        cases_roll_std_3=float(record.get('cases_roll_std_3')) if record.get('cases_roll_std_3') else None,
                        cases_roll_std_7=float(record.get('cases_roll_std_7')) if record.get('cases_roll_std_7') else None,
                        cases_roll_std_14=float(record.get('cases_roll_std_14')) if record.get('cases_roll_std_14') else None
                    )
                    
                    successful += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing record: {e}")
                    failed += 1
                    continue
            
            # Log sync operation
            sync_end = datetime.now()
            self.db.log_sync('disease_cases', successful, 0, sync_start, sync_end, 'SUCCESS')
            
            logger.info(f"Disease cases sync complete: {successful} synced, {failed} failed out of {total}")
            
            return successful, failed, total
            
        except Exception as e:
            logger.error(f"Error in disease cases sync: {e}")
            sync_end = datetime.now()
            self.db.log_sync('disease_cases', 0, 0, sync_start, sync_end, 'FAILED', str(e))
            return 0, len(cases_data) if cases_data else 0, len(cases_data) if cases_data else 0

    def get_athena_table_stats(self, table_name: str) -> Optional[Dict]:
        """
        Get statistics for an Athena table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table statistics or None
        """
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT date) as distinct_dates,
            MIN(date) as earliest_date,
            MAX(date) as latest_date
        FROM {table_name}
        """
        
        result = self.execute_query(query)
        
        if result and result['results']:
            return result['results'][0]
        
        return None


# Standalone functions for easy integration

def sync_athena_to_postgresql(aws_access_key: str, aws_secret_key: str) -> Tuple[int, int, int]:
    """Sync all Athena disease data to PostgreSQL"""
    try:
        athena = AthenaIntegration(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        return athena.sync_disease_cases_to_postgresql()
    except Exception as e:
        logger.error(f"Failed to sync Athena data: {e}")
        return 0, 0, 0


if __name__ == "__main__":
    # Example usage
    athena = AthenaIntegration(
        aws_access_key_id='YOUR_AWS_ACCESS_KEY',
        aws_secret_access_key='YOUR_AWS_SECRET_KEY',
        region_name='us-east-1',
        s3_output_location='s3://your-bucket/athena-results/'
    )
    
    # Example: Get outbreak alerts
    alerts = athena.get_outbreak_alerts(threshold_zscore=2.5)
    if alerts:
        print("Potential Outbreaks:")
        for alert in alerts[:5]:
            print(f"  {alert.get('district')} - {alert.get('disease')}: Z-score = {alert.get('zscore')}")
    
    # Example: Get table statistics
    stats = athena.get_athena_table_stats('disease_cases_table')
    if stats:
        print(f"\nTable Statistics:")
        print(f"  Total rows: {stats.get('total_rows')}")
        print(f"  Date range: {stats.get('earliest_date')} to {stats.get('latest_date')}")
