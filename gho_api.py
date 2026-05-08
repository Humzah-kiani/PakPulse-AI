import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
from db_config import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GHOIntegration:
    """Integration with WHO Global Health Observatory API"""
    
    # GHO API documentation: https://www.who.int/data/gho
    # Common indicators for disease outbreak detection
    RELEVANT_INDICATORS = {
        'INCIDENCE': 'Incidence of reportable diseases',
        'MORTALITY': 'Mortality rates',
        'CFR': 'Case fatality rate',
        'ACCESS_SANITATION': 'Access to sanitation facilities',
        'MALNUTRITION': 'Prevalence of malnutrition',
        'VACCINATION': 'Vaccination coverage rates',
        'HEALTHCARE_ACCESS': 'Access to healthcare services'
    }
    
    def __init__(self):
        """Initialize GHO API integration"""
        self.base_url = "https://ghoapi.azureedge.net/api"
        self.db = DatabaseConnection()
        self.timeout = 10

    def _log_api_call(self, endpoint: str, status_code: int, 
                     response_time: int, records: int, error: str = None):
        """Log API call to database"""
        try:
            self.db.log_api_call('GHO', endpoint, status_code, 
                               response_time, records, error)
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")

    def get_indicators(self) -> Optional[List[Dict]]:
        """
        Get available health indicators from GHO
        
        Returns:
            List of indicator dictionaries or None if failed
        """
        endpoint = f"{self.base_url}/Indicator"
        
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=self.timeout)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                indicators = data.get('value', [])
                self._log_api_call(endpoint, 200, response_time, len(indicators))
                return indicators
            else:
                error_msg = f"HTTP {response.status_code}"
                self._log_api_call(endpoint, response.status_code, response_time, 0, error_msg)
                logger.warning(f"GHO API returned {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching indicators: {e}")
            self._log_api_call(endpoint, 0, 0, 0, str(e))
            return None

    def get_indicator_data(self, indicator_code: str, year: int = None,
                          region: str = None) -> Optional[List[Dict]]:
        """
        Get data for a specific indicator
        
        Args:
            indicator_code: WHO indicator code (e.g., 'WHOSIS_000001')
            year: Specific year (optional)
            region: WHO region code (optional)
            
        Returns:
            List of data records or None
        """
        endpoint = f"{self.base_url}/Indicator/{indicator_code}/DimensionInd/REGION"
        
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=self.timeout)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('value', [])
                self._log_api_call(endpoint, 200, response_time, len(records))
                return records
            else:
                error_msg = f"HTTP {response.status_code}"
                self._log_api_call(endpoint, response.status_code, response_time, 0, error_msg)
                return None
                
        except Exception as e:
            logger.error(f"Error fetching indicator data for {indicator_code}: {e}")
            self._log_api_call(endpoint, 0, 0, 0, str(e))
            return None

    def get_country_health_profile(self, country_code: str) -> Optional[Dict]:
        """
        Get a health indicator profile for a specific country using WHO GHO OData.

        Args:
            country_code: ISO country code (e.g., 'PAK' for Pakistan)

        Returns:
            Dictionary of indicators to latest values (or None on total failure)
        """
        # Because WHO GHO has dozens of indicator entity sets, use the Indicator endpoint
        # to find relevant indicator codes and then fetch values filtered by country.
        try:
            indicators_response = requests.get(f"{self.base_url}/Indicator", timeout=self.timeout)
            if indicators_response.status_code != 200:
                logger.warning(f"Failed to fetch indicators list: {indicators_response.status_code}")
                return None

            indicators_data = indicators_response.json().get('value', [])

            # Pick relevant indicators from the full list by keyword in name.
            keywords = ['incidence', 'mortality', 'cfr', 'sanitation', 'malnutrition', 'vaccination', 'healthcare', 'health care', 'access']
            relevant_codes = [x.get('IndicatorCode') for x in indicators_data
                              if any(k in (x.get('IndicatorName') or '').lower() for k in keywords)]

            profile = {}
            fetched = 0

            for indicator_code in relevant_codes:
                if not indicator_code:
                    continue

                # Query indicator entity for country data.
                query_url = f"https://ghoapi.azureedge.net/api/{indicator_code}?$filter=SpatialDim%20eq%20%27{country_code}%27&$orderby=TimeDim%20desc&$top=1"
                start_time = time.time()
                response = requests.get(query_url, timeout=self.timeout)
                duration_ms = int((time.time() - start_time) * 1000)

                if response.status_code != 200:
                    continue

                data = response.json().get('value', [])
                self._log_api_call(query_url, response.status_code, duration_ms, len(data))

                if not data:
                    continue

                # Use latest data point
                point = data[0]
                value = point.get('NumericValue') if point.get('NumericValue') is not None else point.get('Value')
                if value is not None:
                    profile[indicator_code] = {
                        'indicator_name': next((x.get('IndicatorName') for x in indicators_data if x.get('IndicatorCode') == indicator_code), indicator_code),
                        'value': value,
                        'year': point.get('TimeDim'),
                        'source': point.get('DataSourceDim') or 'WHO GHO'
                    }
                    fetched += 1

                # Limit amount for performance
                if fetched >= 20:
                    break

            return profile if profile else None

        except Exception as e:
            logger.error(f"Error fetching country profile for {country_code}: {e}")
            return None

    def fetch_disease_incidence(self, disease_code: str, country_code: str = 'PAK',
                               year: int = None) -> Optional[Dict]:
        """
        Fetch disease incidence data
        
        Args:
            disease_code: WHO disease code
            country_code: ISO country code
            year: Specific year or None for latest
            
        Returns:
            Dictionary with incidence data or None
        """
        # This would typically require specific indicator codes from WHO
        # Common disease-related indicators should be used
        logger.info(f"Fetching incidence data for disease {disease_code} in {country_code}")
        
        # Example implementation - actual codes would depend on WHO's specific indicators
        try:
            data = self.get_indicator_data(disease_code, year)
            if data:
                return self._parse_incidence_data(data, country_code)
        except Exception as e:
            logger.error(f"Error fetching disease incidence: {e}")
        
        return None

    def fetch_health_risk_factors(self, country_code: str = 'PAK') -> Optional[Dict]:
        """
        Fetch health risk factors (sanitation, nutrition, access to healthcare)
        
        Args:
            country_code: ISO country code
            
        Returns:
            Dictionary with risk factor data
        """
        risk_factors = {}
        
        # Relevant indicator codes for health risk assessment
        indicator_codes = {
            'SANITATION': 'SDG_06.2.1.C',  # Access to sanitation
            'CLEAN_WATER': 'SDG_06.1.1',   # Access to clean water
            'MALNUTRITION': 'SDG_02.2.1.B', # Prevalence of stunting
            'HEALTHCARE_ACCESS': 'UHC_SERVICE_COVERAGE', # UHC service coverage
        }
        
        for key, code in indicator_codes.items():
            try:
                data = self.get_indicator_data(code)
                if data:
                    risk_factors[key] = data
            except Exception as e:
                logger.warning(f"Could not fetch {key} data: {e}")
        
        return risk_factors if risk_factors else None

    def store_health_indicator(self, year: int, indicator_name: str,
                              indicator_code: str, value: float, unit: str,
                              district_name: str = None, disease_name: str = None):
        """
        Store health indicator in database
        
        Args:
            year: Data year
            indicator_name: Human-readable indicator name
            indicator_code: WHO indicator code
            value: Indicator value
            unit: Unit of measurement
            district_name: District name (optional)
            disease_name: Disease name (optional)
        """
        try:
            district_id = None
            disease_id = None
            
            if district_name:
                district = self.db.get_district_by_name(district_name)
                district_id = district['district_id'] if district else None
            
            if disease_name:
                disease = self.db.get_disease_by_name(disease_name)
                disease_id = disease['disease_id'] if disease else None
            
            self.db.insert_health_indicator(
                year=year,
                indicator_name=indicator_name,
                indicator_code=indicator_code,
                value=value,
                unit=unit,
                data_source='WHO GHO',
                district_id=district_id,
                disease_id=disease_id
            )
            
            logger.info(f"Stored health indicator: {indicator_name}")
            
        except Exception as e:
            logger.error(f"Error storing health indicator: {e}")

    def _parse_incidence_data(self, raw_data: List[Dict], 
                             country_code: str) -> Optional[Dict]:
        """
        Parse incidence data from GHO API
        
        Args:
            raw_data: Raw API response
            country_code: Country code to filter
            
        Returns:
            Parsed incidence data or None
        """
        try:
            parsed = {}
            
            for record in raw_data:
                if record.get('SpatialDim') == country_code:
                    year = record.get('TimeDim')
                    value = float(record.get('Value', 0))
                    
                    if year not in parsed:
                        parsed[year] = value
            
            return parsed if parsed else None
            
        except Exception as e:
            logger.error(f"Error parsing incidence data: {e}")
            return None

    def fetch_and_store_country_indicators(self, country_code: str = 'PAK',
                                          year: int = None) -> Tuple[int, int]:
        """
        Fetch and store key health indicators for a country
        
        Args:
            country_code: ISO country code
            year: Year to fetch (default: latest)
            
        Returns:
            Tuple of (successfully stored, failed)
        """
        successful = 0
        failed = 0
        
        try:
            profile = self.get_country_health_profile(country_code)
            
            if not profile:
                logger.warning(f"Could not fetch profile for {country_code}")
                return 0, 1
            
            # Store key indicators from profile
            for key, item in profile.items():
                try:
                    if isinstance(item, dict) and 'value' in item:
                        numeric_val = float(item.get('value', 0))
                        self.store_health_indicator(
                            year=item.get('year') or year or datetime.now().year,
                            indicator_name=item.get('indicator_name', key),
                            indicator_code=key,
                            value=numeric_val,
                            unit='As reported'
                        )
                        successful += 1
                    elif isinstance(item, (int, float)):
                        self.store_health_indicator(
                            year=year or datetime.now().year,
                            indicator_name=key,
                            indicator_code=key,
                            value=float(item),
                            unit='As reported'
                        )
                        successful += 1
                except Exception as e:
                    logger.warning(f"Failed to store indicator {key}: {e}")
                    failed += 1
            
            logger.info(f"Stored country indicators: {successful} successful, {failed} failed")
            
        except Exception as e:
            logger.error(f"Error in fetch and store: {e}")
            failed += 1
        
        return successful, failed

    def generate_risk_alert(self, district_name: str, disease_name: str,
                           threshold: float = 0.7) -> Optional[Dict]:
        """
        Generate outbreak risk alert based on health indicators
        
        Args:
            district_name: District name
            disease_name: Disease name
            threshold: Risk threshold (0-1)
            
        Returns:
            Alert dictionary or None if risk is low
        """
        alert = {
            'district': district_name,
            'disease': disease_name,
            'timestamp': datetime.now().isoformat(),
            'risk_factors': [],
            'overall_risk': 0
        }
        
        # Aggregate risk factors from health indicators
        # This would combine multiple data sources
        
        return alert if alert['overall_risk'] > threshold else None


# Standalone function for easy integration

def fetch_gho_indicators_for_pakistan() -> Tuple[int, int]:
    """Fetch and store GHO health indicators for Pakistan"""
    try:
        gho = GHOIntegration()
        return gho.fetch_and_store_country_indicators('PAK')
    except Exception as e:
        logger.error(f"Failed to fetch GHO indicators: {e}")
        return 0, 1


if __name__ == "__main__":
    # Example usage
    gho = GHOIntegration()
    
    # Get country health profile
    profile = gho.get_country_health_profile('PAK')
    if profile:
        print("Pakistan Health Profile:")
        for key, value in list(profile.items())[:5]:
            print(f"  {key}: {value}")
    
    # Get health risk factors
    risk_factors = gho.fetch_health_risk_factors('PAK')
    if risk_factors:
        print("\nHealth Risk Factors:")
        for factor, data in risk_factors.items():
            print(f"  {factor}: {len(data) if isinstance(data, list) else 'N/A'} records")
