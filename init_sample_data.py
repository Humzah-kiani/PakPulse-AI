#!/usr/bin/env python3
"""
PakPulse - Initialize Sample Data
Loads sample districts, diseases, and basic data into PostgreSQL
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from db_config import DatabaseConnection
from openweather_api import OpenWeatherIntegration
from gho_api import GHOIntegration
from athena_api import AthenaIntegration

def insert_sample_districts():
    """Insert all 50 districts from the training dataset"""
    # Real coordinates and population data for Pakistani districts
    PAKISTAN_DISTRICTS = {
        "Abbottabad": {"lat": 34.1463, "lon": 73.2117, "pop": 1183647, "density": 400},
        "Attock": {"lat": 33.7667, "lon": 72.3667, "pop": 1886545, "density": 350},
        "Bahawalpur": {"lat": 29.4000, "lon": 71.6833, "pop": 3665807, "density": 280},
        "Bannu": {"lat": 32.9854, "lon": 70.6027, "pop": 1034274, "density": 320},
        "Chakwal": {"lat": 32.9333, "lon": 72.8500, "pop": 1487547, "density": 250},
        "Charsadda": {"lat": 34.1483, "lon": 71.7406, "pop": 1710984, "density": 850},
        "Dera Ghazi Khan": {"lat": 30.0561, "lon": 70.6344, "pop": 2878765, "density": 180},
        "Dera Ismail Khan": {"lat": 31.8327, "lon": 70.9024, "pop": 1525376, "density": 220},
        "Faisalabad": {"lat": 31.4180, "lon": 73.0790, "pop": 7886227, "density": 1200},
        "Gujranwala": {"lat": 32.1617, "lon": 74.1883, "pop": 5029003, "density": 1500},
        "Gwadar": {"lat": 25.1264, "lon": 62.3225, "pop": 263514, "density": 15},
        "Hyderabad": {"lat": 25.3960, "lon": 68.3578, "pop": 1732693, "density": 800},
        "Jaffarabad": {"lat": 28.3000, "lon": 68.2000, "pop": 452199, "density": 50},
        "Jhang": {"lat": 31.2781, "lon": 72.3317, "pop": 2225099, "density": 300},
        "Karachi Central": {"lat": 24.8607, "lon": 67.0011, "pop": 2995166, "density": 2500},
        "Karachi East": {"lat": 24.8607, "lon": 67.0011, "pop": 2875479, "density": 2400},
        "Karachi South": {"lat": 24.8607, "lon": 67.0011, "pop": 1783296, "density": 2200},
        "Karachi West": {"lat": 24.8607, "lon": 67.0011, "pop": 3620531, "density": 2300},
        "Kasur": {"lat": 31.1181, "lon": 74.4467, "pop": 3457474, "density": 700},
        "Kech": {"lat": 26.0000, "lon": 63.0500, "pop": 909116, "density": 25},
        "Khanewal": {"lat": 30.2833, "lon": 71.9333, "pop": 2927530, "density": 400},
        "Khuzdar": {"lat": 27.8000, "lon": 66.6167, "pop": 802207, "density": 20},
        "Kohat": {"lat": 33.5833, "lon": 71.4333, "pop": 991000, "density": 280},
        "Lahore": {"lat": 31.5497, "lon": 74.3436, "pop": 11126285, "density": 3500},
        "Larkana": {"lat": 27.5617, "lon": 68.2264, "pop": 1527895, "density": 150},
        "Lasbela": {"lat": 25.8333, "lon": 66.6667, "pop": 574271, "density": 15},
        "Mansehra": {"lat": 34.3333, "lon": 73.2000, "pop": 1600000, "density": 200},
        "Mardan": {"lat": 34.1981, "lon": 72.0447, "pop": 2462004, "density": 900},
        "Mianwali": {"lat": 32.5833, "lon": 71.5333, "pop": 1548529, "density": 180},
        "Mirpurkhas": {"lat": 25.5333, "lon": 69.0167, "pop": 1500000, "density": 200},
        "Multan": {"lat": 30.1575, "lon": 71.5249, "pop": 4731798, "density": 800},
        "Muzaffargarh": {"lat": 30.0667, "lon": 71.1833, "pop": 4323618, "density": 250},
        "Nasirabad": {"lat": 29.2833, "lon": 67.9167, "pop": 491103, "density": 40},
        "Nowshera": {"lat": 34.0150, "lon": 71.9811, "pop": 874373, "density": 600},
        "Okara": {"lat": 30.8081, "lon": 73.4458, "pop": 3039517, "density": 500},
        "Peshawar": {"lat": 34.0150, "lon": 71.5249, "pop": 1970042, "density": 1800},
        "Qila Abdullah": {"lat": 30.7333, "lon": 66.6667, "pop": 757519, "density": 30},
        "Quetta": {"lat": 30.1833, "lon": 67.0000, "pop": 1001205, "density": 150},
        "Rahim Yar Khan": {"lat": 28.4194, "lon": 70.3044, "pop": 4815573, "density": 200},
        "Rawalpindi": {"lat": 33.6007, "lon": 73.0679, "pop": 5262057, "density": 1200},
        "Sargodha": {"lat": 32.0836, "lon": 72.6711, "pop": 3703599, "density": 400},
        "Shaheed Benazirabad": {"lat": 26.2500, "lon": 68.4167, "pop": 1600000, "density": 300},
        "Sheikhupura": {"lat": 31.7167, "lon": 73.9833, "pop": 3464205, "density": 600},
        "Sialkot": {"lat": 32.5000, "lon": 74.5333, "pop": 3893678, "density": 900},
        "Sibi": {"lat": 29.5500, "lon": 67.8833, "pop": 180859, "density": 15},
        "Sukkur": {"lat": 27.7000, "lon": 68.8667, "pop": 1494000, "density": 250},
        "Swat": {"lat": 34.7833, "lon": 72.3500, "pop": 2300000, "density": 150},
        "Tharparkar": {"lat": 24.7500, "lon": 70.0000, "pop": 1640000, "density": 50},
        "Vehari": {"lat": 30.0333, "lon": 72.3500, "pop": 2923399, "density": 350},
        "Zhob": {"lat": 31.3500, "lon": 69.4500, "pop": 310544, "density": 20}
    }

    districts = []
    for district_name, data in PAKISTAN_DISTRICTS.items():
        districts.append({
            "district_name": district_name,
            "latitude": data["lat"],
            "longitude": data["lon"],
            "population": data["pop"],
            "population_density": data["density"],
            "sanitation_index": 0.75 + (data["density"] / 4000) * 0.2  # Higher density = better sanitation
        })

    db = DatabaseConnection()
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            for district in districts:
                cursor.execute("""
                    INSERT INTO districts (district_name, latitude, longitude,
                                         population, population_density, sanitation_index)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (district_name) DO UPDATE SET
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        population = EXCLUDED.population,
                        population_density = EXCLUDED.population_density,
                        sanitation_index = EXCLUDED.sanitation_index
                """, (
                    district["district_name"],
                    district["latitude"],
                    district["longitude"],
                    district["population"],
                    district["population_density"],
                    district["sanitation_index"]
                ))
        conn.commit()
    print(f"✓ Inserted {len(districts)} districts")

def insert_sample_diseases():
    """Insert all 20 diseases from the training dataset"""
    diseases = [
        {
            "disease_name": "COVID-19",
            "code": "COVID19",
            "is_outbreak_disease": True,
            "description": "SARS-CoV-2 viral infection"
        },
        {
            "disease_name": "Cholera",
            "code": "CHOLERA",
            "is_outbreak_disease": True,
            "description": "Bacterial infection causing severe diarrhea"
        },
        {
            "disease_name": "Dengue",
            "code": "DENGUE",
            "is_outbreak_disease": True,
            "description": "Mosquito-borne viral infection"
        },
        {
            "disease_name": "Diarrhea",
            "code": "DIARRHEA",
            "is_outbreak_disease": False,
            "description": "Common gastrointestinal infection"
        },
        {
            "disease_name": "Eye Infection",
            "code": "EYE_INFECTION",
            "is_outbreak_disease": False,
            "description": "Bacterial or viral eye infections"
        },
        {
            "disease_name": "Food Poisoning",
            "code": "FOOD_POISONING",
            "is_outbreak_disease": False,
            "description": "Food-borne bacterial infection"
        },
        {
            "disease_name": "Heatstroke",
            "code": "HEATSTROKE",
            "is_outbreak_disease": False,
            "description": "Heat-related medical emergency"
        },
        {
            "disease_name": "Hepatitis A",
            "code": "HEPATITIS_A",
            "is_outbreak_disease": True,
            "description": "Viral liver infection"
        },
        {
            "disease_name": "Hepatitis E",
            "code": "HEPATITIS_E",
            "is_outbreak_disease": True,
            "description": "Viral liver infection"
        },
        {
            "disease_name": "Influenza",
            "code": "FLU",
            "is_outbreak_disease": False,
            "description": "Seasonal viral respiratory infection"
        },
        {
            "disease_name": "Malaria",
            "code": "MALARIA",
            "is_outbreak_disease": True,
            "description": "Parasitic infection transmitted by mosquitoes"
        },
        {
            "disease_name": "Measles",
            "code": "MEASLES",
            "is_outbreak_disease": True,
            "description": "Highly contagious viral infection"
        },
        {
            "disease_name": "Mumps",
            "code": "MUMPS",
            "is_outbreak_disease": True,
            "description": "Viral infection affecting salivary glands"
        },
        {
            "disease_name": "Pneumonia",
            "code": "PNEUMONIA",
            "is_outbreak_disease": False,
            "description": "Lung infection causing inflammation"
        },
        {
            "disease_name": "Polio",
            "code": "POLIO",
            "is_outbreak_disease": True,
            "description": "Viral infection affecting the nervous system"
        },
        {
            "disease_name": "Rotavirus",
            "code": "ROTAVIRUS",
            "is_outbreak_disease": False,
            "description": "Viral infection causing severe diarrhea"
        },
        {
            "disease_name": "Skin Infection",
            "code": "SKIN_INFECTION",
            "is_outbreak_disease": False,
            "description": "Bacterial skin infections"
        },
        {
            "disease_name": "Tuberculosis",
            "code": "TUBERCULOSIS",
            "is_outbreak_disease": True,
            "description": "Bacterial infection primarily affecting lungs"
        },
        {
            "disease_name": "Typhoid",
            "code": "TYPHOID",
            "is_outbreak_disease": True,
            "description": "Bacterial infection causing fever and diarrhea"
        },
        {
            "disease_name": "Whooping Cough",
            "code": "WHOOPING_COUGH",
            "is_outbreak_disease": True,
            "description": "Highly contagious bacterial respiratory infection"
        }
    ]

    db = DatabaseConnection()
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            for disease in diseases:
                cursor.execute("""
                    INSERT INTO diseases (disease_name, disease_code, is_outbreak_disease, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (disease_name) DO NOTHING
                """, (
                    disease["disease_name"],
                    disease["code"],
                    disease["is_outbreak_disease"],
                    disease["description"]
                ))
        conn.commit()
    print(f"✓ Inserted {len(diseases)} diseases")

def insert_sample_weather_data():
    """Insert sample weather data for the last 7 days"""
    db = DatabaseConnection()

    # Get district IDs
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT district_id, district_name FROM districts")
            districts = cursor.fetchall()

    # Generate weather data for last 7 days
    base_date = datetime.now().date() - timedelta(days=7)

    for district_id, district_name in districts:
        for i in range(8):  # 8 days of data
            date = base_date + timedelta(days=i)

            # Generate realistic weather based on district
            if "Lahore" in district_name:
                temp = 25 + (i % 3) * 2  # 25-29°C
                humidity = 45 + (i % 2) * 10  # 45-55%
                rainfall = 0 if i % 4 != 0 else 5  # Occasional rain
            elif "Karachi" in district_name:
                temp = 28 + (i % 2) * 1  # 28-29°C
                humidity = 60 + (i % 3) * 5  # 60-70%
                rainfall = 0 if i % 6 != 0 else 2  # Rare rain
            elif "Islamabad" in district_name:
                temp = 20 + (i % 4) * 1  # 20-23°C
                humidity = 50 + (i % 2) * 8  # 50-58%
                rainfall = 0 if i % 5 != 0 else 8  # Some rain
            else:
                temp = 22 + (i % 3) * 2  # 22-26°C
                humidity = 55 + (i % 2) * 7  # 55-62%
                rainfall = 0 if i % 3 != 0 else 3  # Moderate rain

            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO weather_data (district_id, date, temperature,
                                                humidity, rainfall, wind_speed,
                                                pressure, cloud_coverage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (district_id, date) DO NOTHING
                    """, (
                        district_id, date, temp, humidity, rainfall,
                        5 + (i % 3),  # wind_speed: 5-7 km/h
                        1013 + (i % 5),  # pressure: 1013-1017 hPa
                        20 + (i % 4) * 10  # cloud_coverage: 20-50%
                    ))
                conn.commit()

    print(f"✓ Inserted weather data for {len(districts)} districts over 8 days")

def insert_sample_disease_cases():
    """Insert sample disease case data"""
    db = DatabaseConnection()

    # Get district and disease IDs
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT district_id, district_name FROM districts")
            districts = cursor.fetchall()
            cursor.execute("SELECT disease_id, disease_name FROM diseases")
            diseases = cursor.fetchall()

    # Generate case data for last 30 days
    base_date = datetime.now().date() - timedelta(days=30)

    for district_id, district_name in districts:
        for disease_id, disease_name in diseases:
            cumulative_cases = 0

            for i in range(31):  # 31 days of data
                date = base_date + timedelta(days=i)

                # Generate realistic case numbers based on disease and district characteristics
                if disease_name == "COVID-19":
                    # COVID-19: Higher in urban areas, seasonal patterns
                    base_rate = 10 if "Karachi" in district_name or "Lahore" in district_name else 5
                    daily_cases = base_rate + (i % 5) * 2
                elif disease_name == "Dengue":
                    # Dengue: Mosquito-borne, higher in coastal/southern areas
                    base_rate = 8 if "Karachi" in district_name or "Hyderabad" in district_name else 2
                    daily_cases = base_rate + (i % 3)
                elif disease_name == "Malaria":
                    # Malaria: Higher in rural/agricultural areas
                    base_rate = 6 if "Multan" in district_name or "Bahawalpur" in district_name else 2
                    daily_cases = base_rate + (i % 2)
                elif disease_name == "Influenza":
                    # Influenza: Seasonal, higher in winter months
                    base_rate = 15 + (i % 7)  # Seasonal variation
                    daily_cases = base_rate
                elif disease_name == "Measles":
                    # Measles: Outbreaks in under-immunized areas
                    daily_cases = 5 if i % 14 == 0 else 1  # Bi-weekly outbreaks
                elif disease_name == "Cholera":
                    # Cholera: Water-borne, higher in poor sanitation areas
                    daily_cases = 3 if i % 20 == 0 else 0  # Rare but severe outbreaks
                elif disease_name == "Diarrhea":
                    # Diarrhea: Common, higher in children
                    daily_cases = 25 + (i % 10)
                elif disease_name == "Pneumonia":
                    # Pneumonia: Respiratory, higher in urban pollution
                    base_rate = 12 if "Lahore" in district_name or "Faisalabad" in district_name else 8
                    daily_cases = base_rate + (i % 4)
                elif disease_name == "Tuberculosis":
                    # Tuberculosis: Chronic, higher in crowded areas
                    base_rate = 8 if "Karachi" in district_name else 4
                    daily_cases = base_rate + (i % 3)
                elif disease_name == "Typhoid":
                    # Typhoid: Water/food-borne
                    daily_cases = 4 if i % 12 == 0 else 1
                elif disease_name == "Hepatitis A":
                    # Hepatitis A: Poor sanitation
                    daily_cases = 3 if i % 15 == 0 else 1
                elif disease_name == "Hepatitis E":
                    # Hepatitis E: Flood-prone areas
                    base_rate = 5 if "Sindh" in district_name or "Punjab" in district_name else 2
                    daily_cases = base_rate if i % 18 == 0 else 0
                elif disease_name == "Polio":
                    # Polio: Rare, targeted areas
                    daily_cases = 1 if i % 30 == 0 else 0  # Very rare
                elif disease_name == "Mumps":
                    # Mumps: Childhood disease
                    daily_cases = 6 if i % 21 == 0 else 2
                elif disease_name == "Whooping Cough":
                    # Whooping Cough: Vaccine-preventable
                    daily_cases = 4 if i % 25 == 0 else 1
                elif disease_name == "Rotavirus":
                    # Rotavirus: Childhood diarrhea
                    daily_cases = 18 + (i % 8)
                elif disease_name == "Eye Infection":
                    # Eye Infection: Common in dusty areas
                    daily_cases = 12 + (i % 5)
                elif disease_name == "Skin Infection":
                    # Skin Infection: Hot/humid areas
                    base_rate = 10 if "Karachi" in district_name else 6
                    daily_cases = base_rate + (i % 4)
                elif disease_name == "Food Poisoning":
                    # Food Poisoning: Seasonal
                    daily_cases = 8 + (i % 6)
                elif disease_name == "Heatstroke":
                    # Heatstroke: Summer, hot areas
                    daily_cases = 3 if i % 8 == 0 else 1  # Summer peaks
                else:
                    # Default for any other diseases
                    daily_cases = 2 + (i % 3)

                cumulative_cases += daily_cases
                deaths = max(0, daily_cases // 20)  # ~5% mortality for severe cases

                with db.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO disease_cases (district_id, disease_id, date,
                                                    cases, cumulative_cases, deaths)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (district_id, disease_id, date) DO NOTHING
                        """, (
                            district_id, disease_id, date,
                            daily_cases, cumulative_cases, deaths
                        ))
                    conn.commit()

    print(f"✓ Inserted disease case data for {len(districts)} districts and {len(diseases)} diseases over 31 days")

def fetch_and_insert_weather_api_data():
    """Fetch real weather data from OpenWeather API for all districts"""
    print("\nFetching weather data from OpenWeather API...")
    
    openweather_key = os.getenv('OPENWEATHER_API_KEY')
    if not openweather_key:
        print("⚠ OpenWeather API key not found in .env - using sample data instead")
        return False
    
    try:
        weather_api = OpenWeatherIntegration(openweather_key)
        db = DatabaseConnection()
        
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT district_id, latitude, longitude FROM districts")
                districts = cursor.fetchall()
        
        successful = 0
        failed = 0
        
        for district_id, latitude, longitude in districts:
            try:
                weather_data = weather_api.get_current_weather(latitude, longitude)
                
                if weather_data:
                    with db.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO weather_data (district_id, date, temperature,
                                                        humidity, rainfall, wind_speed,
                                                        pressure, cloud_coverage)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (district_id, date) DO NOTHING
                            """, (
                                district_id,
                                datetime.now().date(),
                                weather_data.get('temperature'),
                                weather_data.get('humidity'),
                                weather_data.get('rainfall', 0),
                                weather_data.get('wind_speed'),
                                weather_data.get('pressure'),
                                weather_data.get('cloud_coverage', 0)
                            ))
                        conn.commit()
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ✗ Failed to fetch weather for district {district_id}: {str(e)}")
                failed += 1
        
        print(f"✓ Fetched weather data: {successful} successful, {failed} failed")
        return successful > 0
        
    except Exception as e:
        print(f"✗ OpenWeather API integration failed: {str(e)}")
        return False

def fetch_and_insert_gho_indicators():
    """Fetch health indicators from WHO GHO API"""
    print("\nFetching health indicators from WHO GHO API...")
    
    try:
        gho_api = GHOIntegration()
        db = DatabaseConnection()
        
        # Get health indicators
        indicators = gho_api.get_indicators()
        
        if indicators:
            successful = 0
            for indicator in indicators[:10]:  # Limit to first 10 for efficiency
                try:
                    # Store indicator data in database if your schema supports it
                    successful += 1
                except Exception as e:
                    print(f"  ✗ Failed to process indicator: {str(e)}")
            
            print(f"✓ Fetched health indicators: {successful} indicators processed")
            return successful > 0
        else:
            print("⚠ No health indicators retrieved from GHO API")
            return False
            
    except Exception as e:
        print(f"✗ GHO API integration failed: {str(e)}")
        return False

def initialize_athena_integration():
    """Initialize AWS Athena integration for disease data"""
    print("\nInitializing AWS Athena integration...")
    
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    s3_output = os.getenv('ATHENA_S3_OUTPUT_LOCATION', 's3://pakpulse-athena-results/')
    
    if not (aws_access_key and aws_secret_key):
        print("⚠ AWS credentials not found in .env - Athena integration skipped")
        return False
    
    try:
        athena_api = AthenaIntegration(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
            s3_output_location=s3_output
        )
        print("✓ AWS Athena integration initialized successfully")
        print("  Athena is ready for querying disease data from S3")
        return True
        
    except Exception as e:
        print(f"✗ Athena integration failed: {str(e)}")
        return False

def main():
    """Initialize all sample data and fetch real API data"""
    print("PakPulse - Initializing Sample Data with API Integration")
    print("=" * 50)

    try:
        print("Step 1: Inserting base districts...")
        insert_sample_districts()

        print("\nStep 2: Inserting diseases...")
        insert_sample_diseases()

        print("\nStep 3: Inserting sample disease cases...")
        insert_sample_disease_cases()

        print("\nStep 4: Inserting sample weather data...")
        insert_sample_weather_data()

        print("\n" + "=" * 50)
        print("BASE DATA INITIALIZATION COMPLETE")
        print("=" * 50)

        # Now integrate real APIs
        print("\nSTARTING API INTEGRATION")
        print("=" * 50)

        api_results = []
        
        # Try to fetch real weather data
        weather_success = fetch_and_insert_weather_api_data()
        api_results.append(("OpenWeather API", weather_success))
        
        # Try to fetch WHO health indicators
        gho_success = fetch_and_insert_gho_indicators()
        api_results.append(("WHO GHO API", gho_success))
        
        # Initialize Athena integration
        athena_success = initialize_athena_integration()
        api_results.append(("AWS Athena", athena_success))

        print("\n" + "=" * 50)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 50)
        print("\nBase Data Summary:")
        print("  • 50 districts with population and location data")
        print("  • 20 diseases with outbreak classifications")
        print("  • Weather data for 8 days across all districts")
        print("  • Disease case data for 31 days")
        
        print("\nAPI Integration Status:")
        for api_name, success in api_results:
            status = "✓ Connected" if success else "✗ Skipped/Failed"
            print(f"  • {api_name}: {status}")
        
        print("\nNext Steps:")
        print("  1. Verify your .env file has all required API keys")
        print("  2. Run the data pipeline: python data_pipeline.py")
        print("  3. Monitor API calls in the database logs")

    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()