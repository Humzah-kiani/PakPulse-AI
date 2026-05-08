#!/usr/bin/env python3
"""
Check database contents after initialization
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_config import DatabaseConnection

def check_database():
    db = DatabaseConnection()
    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Check districts
        cursor.execute('SELECT COUNT(*) FROM districts')
        district_count = cursor.fetchone()[0]
        print(f"Districts: {district_count}")

        # Check diseases
        cursor.execute('SELECT COUNT(*) FROM diseases')
        disease_count = cursor.fetchone()[0]
        print(f"Diseases: {disease_count}")

        # List diseases
        cursor.execute('SELECT disease_name FROM diseases ORDER BY disease_name')
        diseases = cursor.fetchall()
        print("\nDiseases loaded:")
        for disease in diseases:
            print(f"  - {disease[0]}")

        # Check disease cases
        cursor.execute('SELECT COUNT(*) FROM disease_cases')
        case_count = cursor.fetchone()[0]
        print(f"\nDisease cases: {case_count}")

        # Calculate expected cases: 50 districts × 20 diseases × 31 days
        expected_cases = 50 * 20 * 31
        print(f"Expected cases: {expected_cases}")

if __name__ == "__main__":
    check_database()