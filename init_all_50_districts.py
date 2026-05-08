#!/usr/bin/env python3
"""
PakPulse - Initialize All 50 Districts
Loads all 50 districts from the dataset with real coordinates and population data
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

def insert_all_districts():
    """Insert all 50 districts with real data"""
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
    print(f"✓ Inserted/Updated {len(districts)} districts with real coordinates and population data")

def insert_sample_diseases():
    """Insert sample diseases (same as before)"""
    diseases = [
        {
            "disease_name": "COVID-19",
            "code": "COVID19",
            "is_outbreak_disease": True,
            "description": "SARS-CoV-2 viral infection"
        },
        {
            "disease_name": "Dengue",
            "code": "DENGUE",
            "is_outbreak_disease": True,
            "description": "Mosquito-borne viral infection"
        },
        {
            "disease_name": "Malaria",
            "code": "MALARIA",
            "is_outbreak_disease": True,
            "description": "Parasitic infection transmitted by mosquitoes"
        },
        {
            "disease_name": "Influenza",
            "code": "FLU",
            "is_outbreak_disease": False,
            "description": "Seasonal viral respiratory infection"
        },
        {
            "disease_name": "Measles",
            "code": "MEASLES",
            "is_outbreak_disease": True,
            "description": "Highly contagious viral infection"
        },
        {
            "disease_name": "Cholera",
            "code": "CHOLERA",
            "is_outbreak_disease": True,
            "description": "Bacterial infection causing severe diarrhea"
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

def insert_weather_data_for_all_districts():
    """Insert sample weather data for all 50 districts"""
    db = DatabaseConnection()

    # Get all district IDs
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT district_id, district_name, latitude, longitude FROM districts")
            districts = cursor.fetchall()

    # Generate weather data for last 7 days
    base_date = datetime.now().date() - timedelta(days=7)

    total_weather_records = 0
    for district_id, district_name, lat, lon in districts:
        for i in range(8):  # 8 days of data
            date = base_date + timedelta(days=i)

            # Generate realistic weather based on latitude and district characteristics
            base_temp = 25 - (lat - 24) * 0.3  # Southern districts are warmer
            temp = base_temp + (i % 3) * 1  # Daily variation

            # Humidity based on coastal vs inland
            if "Karachi" in district_name or "Gwadar" in district_name or "Lasbela" in district_name:
                humidity = 65 + (i % 2) * 10  # Coastal areas more humid
                rainfall = 0 if i % 5 != 0 else 3  # Occasional rain
            elif lat > 32:  # Northern areas
                humidity = 50 + (i % 2) * 8
                rainfall = 0 if i % 3 != 0 else 5  # More rain in north
            else:  # Central/Southern
                humidity = 45 + (i % 2) * 12
                rainfall = 0 if i % 4 != 0 else 2  # Moderate rain

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
            total_weather_records += 1

    print(f"✓ Inserted {total_weather_records} weather records for {len(districts)} districts over 8 days")

def insert_disease_cases_for_all_districts():
    """Insert sample disease case data for all 50 districts"""
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

    total_case_records = 0
    for district_id, district_name in districts:
        # Get district latitude for weather-based case generation
        district_lat = PAKISTAN_DISTRICTS.get(district_name, {}).get("lat", 30.0)

        for disease_id, disease_name in diseases:
            cumulative_cases = 0

            for i in range(31):  # 31 days of data
                date = base_date + timedelta(days=i)

                # Generate realistic case numbers based on disease, district, and population
                district_info = PAKISTAN_DISTRICTS.get(district_name, {"pop": 1000000})
                population_factor = district_info["pop"] / 1000000  # Normalize to million

                if disease_name == "COVID-19":
                    base_cases = 5 * population_factor
                    daily_cases = int(base_cases + (i % 3) * population_factor)
                elif disease_name == "Dengue":
                    # Higher in Karachi and southern districts
                    if any(x in district_name for x in ["Karachi", "Hyderabad", "Sukkur", "Larkana"]):
                        daily_cases = int((3 + i % 2) * population_factor * 2)
                    else:
                        daily_cases = int((1 + i % 1) * population_factor)
                elif disease_name == "Malaria":
                    # Higher in southern and rural districts
                    if district_lat < 30 or "Khan" in district_name:
                        daily_cases = int((2 + i % 2) * population_factor * 1.5)
                    else:
                        daily_cases = int((1 + i % 1) * population_factor)
                elif disease_name == "Influenza":
                    daily_cases = int((8 + i % 4) * population_factor)
                elif disease_name == "Measles":
                    daily_cases = 1 if i % 7 == 0 else 0  # Weekly outbreaks
                else:  # Cholera
                    daily_cases = 0 if i % 10 != 0 else int(population_factor)  # Rare outbreaks

                cumulative_cases += daily_cases
                deaths = max(0, int(daily_cases * 0.05))  # ~5% mortality for severe cases

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
                total_case_records += 1

    print(f"✓ Inserted {total_case_records} disease case records for {len(districts)} districts and {len(diseases)} diseases over 31 days")

def main():
    """Initialize all 50 districts with comprehensive data"""
    print("PakPulse - Initializing All 50 Districts")
    print("=" * 50)

    try:
        print("Inserting all 50 districts with real coordinates...")
        insert_all_districts()

        print("Inserting diseases...")
        insert_sample_diseases()

        print("Inserting weather data for all districts...")
        insert_weather_data_for_all_districts()

        print("Inserting disease cases for all districts...")
        insert_disease_cases_for_all_districts()

        print("\n" + "=" * 50)
        print("✅ Complete initialization successful!")
        print("Your database now contains:")
        print("  • 50 districts with real coordinates and population data")
        print("  • 6 diseases with outbreak classifications")
        print("  • Weather data for 8 days across all 50 districts")
        print("  • Disease case data for 31 days across all districts")
        print("\n🚀 Ready to run the full data pipeline for all 50 districts!")

    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()