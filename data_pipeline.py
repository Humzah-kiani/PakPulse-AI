import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Tuple
import os
from dotenv import load_dotenv

from db_config import DatabaseConnection
from openweather_api import OpenWeatherIntegration, fetch_current_weather_for_all_districts
from gho_api import GHOIntegration, fetch_gho_indicators_for_pakistan
from athena_api import AthenaIntegration, sync_athena_to_postgresql

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataPipelineOrchestrator:
    """Orchestrates data fetching and storage from all APIs"""
    
    def __init__(self):
        """Initialize the data pipeline orchestrator"""
        self.db = DatabaseConnection()
        
        # Initialize API integrations
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.s3_output = os.getenv('ATHENA_S3_OUTPUT_LOCATION', 's3://pakpulse-athena-results/')
        
        self.weather_api = None
        self.gho_api = None
        self.athena_api = None
        
        self._initialize_apis()
        
        logger.info("Data Pipeline Orchestrator initialized")

    def _initialize_apis(self):
        """Initialize all API integrations"""
        try:
            if self.openweather_key:
                self.weather_api = OpenWeatherIntegration(self.openweather_key)
                logger.info("OpenWeather API initialized")
            else:
                logger.warning("OpenWeather API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize OpenWeather API: {e}")
        
        try:
            self.gho_api = GHOIntegration()
            logger.info("GHO API initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GHO API: {e}")
        
        try:
            if self.aws_access_key and self.aws_secret_key:
                self.athena_api = AthenaIntegration(
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region,
                    s3_output_location=self.s3_output
                )
                logger.info("Athena API initialized")
            else:
                logger.warning("AWS credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Athena API: {e}")

    # =====================================================
    # WEATHER DATA PIPELINE
    # =====================================================

    def fetch_weather_data(self) -> Tuple[int, int, int]:
        """
        Fetch weather data from OpenWeather API for all districts
        
        Returns:
            Tuple of (successful, failed, total)
        """
        logger.info("Starting weather data fetch...")
        
        if not self.weather_api:
            logger.error("Weather API not initialized")
            return 0, 0, 0
        
        try:
            districts = self.db.get_all_districts()
            
            if not districts:
                logger.warning("No districts found in database")
                return 0, 0, 0
            
            successful, failed, total = self.weather_api.fetch_and_store_weather(districts)
            
            logger.info(f"Weather data fetch complete: {successful}/{total} successful")
            
            return successful, failed, total
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return 0, len(districts) if districts else 0, len(districts) if districts else 0

    # =====================================================
    # HEALTH INDICATORS PIPELINE
    # =====================================================

    def fetch_health_indicators(self) -> Tuple[int, int]:
        """
        Fetch health indicators from GHO API
        
        Returns:
            Tuple of (successful, failed)
        """
        logger.info("Starting health indicators fetch...")
        
        if not self.gho_api:
            logger.error("GHO API not initialized")
            return 0, 1
        
        try:
            successful, failed = self.gho_api.fetch_and_store_country_indicators(
                country_code='PAK',
                year=datetime.now().year
            )
            
            logger.info(f"Health indicators fetch complete: {successful} successful, {failed} failed")
            
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error fetching health indicators: {e}")
            return 0, 1

    # =====================================================
    # DISEASE DATA PIPELINE
    # =====================================================

    def sync_disease_cases(self, days_back: int = 30) -> Tuple[int, int, int]:
        """
        Sync disease cases from Athena to PostgreSQL
        
        Args:
            days_back: Number of days to sync from today
            
        Returns:
            Tuple of (successful, failed, total)
        """
        logger.info(f"Starting disease cases sync (last {days_back} days)...")
        
        if not self.athena_api:
            logger.error("Athena API not initialized")
            return 0, 0, 0
        
        try:
            start_date = datetime.now() - timedelta(days=days_back)
            end_date = datetime.now()
            
            successful, failed, total = self.athena_api.sync_disease_cases_to_postgresql(
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(f"Disease cases sync complete: {successful}/{total} successful")
            
            return successful, failed, total
            
        except Exception as e:
            logger.error(f"Error syncing disease cases: {e}")
            return 0, 0, 0

    # =====================================================
    # RISK ASSESSMENT PIPELINE
    # =====================================================

    def assess_outbreak_risk(self) -> int:
        """
        Assess outbreak risk for all districts and diseases
        
        Returns:
            Number of high-risk alerts
        """
        logger.info("Starting outbreak risk assessment...")
        
        if not self.athena_api:
            logger.error("Athena API not initialized")
            return 0
        
        try:
            alerts = self.athena_api.get_outbreak_alerts(threshold_zscore=2.5)
            
            if alerts:
                logger.info(f"Found {len(alerts)} potential outbreaks")
                
                # Log alerts to database
                for alert in alerts:
                    try:
                        district = self.db.get_district_by_name(alert.get('district'))
                        disease = self.db.get_disease_by_name(alert.get('disease'))
                        
                        if district and disease:
                            logger.warning(
                                f"OUTBREAK ALERT: {alert.get('district')} - "
                                f"{alert.get('disease')} (Z-score: {alert.get('zscore')})"
                            )
                    except Exception as e:
                        logger.error(f"Error processing alert: {e}")
                
                return len(alerts)
            else:
                logger.info("No outbreak alerts at this time")
                return 0
                
        except Exception as e:
            logger.error(f"Error assessing outbreak risk: {e}")
            return 0

    # =====================================================
    # COMPLETE PIPELINE EXECUTION
    # =====================================================

    def run_full_pipeline(self) -> dict:
        """
        Run the complete data pipeline
        
        Returns:
            Dictionary with pipeline execution results
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL DATA PIPELINE EXECUTION")
        logger.info("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'weather': None,
            'health_indicators': None,
            'disease_cases': None,
            'outbreak_alerts': None,
            'total_duration': 0
        }
        
        pipeline_start = time.time()
        
        # Step 1: Fetch weather data
        try:
            logger.info("\n[1/4] Fetching weather data...")
            weather_results = self.fetch_weather_data()
            results['weather'] = {
                'successful': weather_results[0],
                'failed': weather_results[1],
                'total': weather_results[2]
            }
        except Exception as e:
            logger.error(f"Weather pipeline failed: {e}")
            results['weather'] = {'error': str(e)}
        
        # Step 2: Fetch health indicators
        try:
            logger.info("\n[2/4] Fetching health indicators...")
            gho_results = self.fetch_health_indicators()
            results['health_indicators'] = {
                'successful': gho_results[0],
                'failed': gho_results[1]
            }
        except Exception as e:
            logger.error(f"Health indicators pipeline failed: {e}")
            results['health_indicators'] = {'error': str(e)}
        
        # Step 3: Sync disease cases
        try:
            logger.info("\n[3/4] Syncing disease cases...")
            disease_results = self.sync_disease_cases(days_back=30)
            results['disease_cases'] = {
                'successful': disease_results[0],
                'failed': disease_results[1],
                'total': disease_results[2]
            }
        except Exception as e:
            logger.error(f"Disease cases pipeline failed: {e}")
            results['disease_cases'] = {'error': str(e)}
        
        # Step 4: Assess outbreak risk
        try:
            logger.info("\n[4/4] Assessing outbreak risk...")
            alert_count = self.assess_outbreak_risk()
            results['outbreak_alerts'] = alert_count
        except Exception as e:
            logger.error(f"Outbreak risk assessment failed: {e}")
            results['outbreak_alerts'] = {'error': str(e)}
        
        results['total_duration'] = time.time() - pipeline_start
        
        logger.info("\n" + "=" * 60)
        logger.info(f"PIPELINE COMPLETE (Duration: {results['total_duration']:.2f}s)")
        logger.info("=" * 60)
        
        return results

    # =====================================================
    # SCHEDULING
    # =====================================================

    def schedule_jobs(self):
        """Schedule recurring data pipeline jobs"""
        
        # Run full pipeline every day at 2 AM
        schedule.every().day.at("02:00").do(self.run_full_pipeline)
        logger.info("Scheduled: Full pipeline daily at 02:00")
        
        # Fetch weather data every 6 hours
        schedule.every(6).hours.do(self.fetch_weather_data)
        logger.info("Scheduled: Weather data fetch every 6 hours")
        
        # Sync disease cases every 12 hours
        schedule.every(12).hours.do(self.sync_disease_cases)
        logger.info("Scheduled: Disease cases sync every 12 hours")
        
        # Assess outbreak risk every 4 hours
        schedule.every(4).hours.do(self.assess_outbreak_risk)
        logger.info("Scheduled: Outbreak risk assessment every 4 hours")

    def run_scheduler(self):
        """Run the scheduler (blocking call)"""
        logger.info("Starting scheduler...")
        self.schedule_jobs()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check for pending jobs every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.db.close_all_connections()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    orchestrator = DataPipelineOrchestrator()
    
    try:
        # Run once immediately
        logger.info("Running pipeline immediately...")
        results = orchestrator.run_full_pipeline()
        
        logger.info("\nPipeline Results:")
        for key, value in results.items():
            logger.info(f"  {key}: {value}")
        
        # Uncomment to run scheduler (continuous execution)
        # orchestrator.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in pipeline: {e}")
    finally:
        orchestrator.cleanup()


if __name__ == "__main__":
    main()
