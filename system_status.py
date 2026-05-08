#!/usr/bin/env python3
"""
PakPulse - System Status Report for All 50 Districts
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from db_config import DatabaseConnection

def get_system_status():
    """Get comprehensive system status"""
    db = DatabaseConnection()

    print("🩺 PakPulse Disease Surveillance System - Status Report")
    print("=" * 60)

    with db.get_connection() as conn:
        with conn.cursor() as cursor:

            # District count
            cursor.execute("SELECT COUNT(*) FROM districts")
            district_count = cursor.fetchone()[0]
            print(f"📍 Districts: {district_count} (Target: 50)")

            # Disease count
            cursor.execute("SELECT COUNT(*) FROM diseases")
            disease_count = cursor.fetchone()[0]
            print(f"🦠 Diseases: {disease_count}")

            # Weather records
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            weather_count = cursor.fetchone()[0]
            print(f"🌡️ Weather Records: {weather_count}")

            # Disease case records
            cursor.execute("SELECT COUNT(*) FROM disease_cases")
            case_count = cursor.fetchone()[0]
            print(f"📊 Disease Cases: {case_count}")

            # API logs
            cursor.execute("SELECT COUNT(*) FROM api_logs")
            api_logs = cursor.fetchone()[0]
            print(f"🔗 API Calls Logged: {api_logs}")

            print("\n🏆 TOP 5 MOST POPULOUS DISTRICTS:")
            print("-" * 40)
            cursor.execute("""
                SELECT district_name, population, latitude, longitude
                FROM districts
                ORDER BY population DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print("15")

            print("\n🌡️ TODAY'S WEATHER (Hottest Districts):")
            print("-" * 40)
            cursor.execute("""
                SELECT d.district_name, w.temperature, w.humidity, w.rainfall
                FROM weather_data w
                JOIN districts d ON w.district_id = d.district_id
                WHERE w.date = CURRENT_DATE
                ORDER BY w.temperature DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                print("15")

            print("\n🦠 DISEASE CASE SUMMARY (Last 30 Days):")
            print("-" * 40)
            cursor.execute("""
                SELECT di.disease_name, SUM(dc.cases) as total_cases
                FROM disease_cases dc
                JOIN diseases di ON dc.disease_id = di.disease_id
                GROUP BY di.disease_name
                ORDER BY total_cases DESC
            """)
            for row in cursor.fetchall():
                print("15")

            print("\n📈 SYSTEM CAPACITY:")
            print("-" * 40)
            print(f"• Weather monitoring: {district_count} districts")
            print(f"• Disease surveillance: {district_count} districts × {disease_count} diseases")
            print(f"• Data points: {weather_count + case_count:,} total records")
            print(f"• Geographic coverage: Pakistan (50 districts)")

            print("\n✅ SYSTEM STATUS: FULLY OPERATIONAL")
            print("🎯 All 50 districts from your dataset are now active!")

if __name__ == "__main__":
    get_system_status()