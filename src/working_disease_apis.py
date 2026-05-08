"""
Working Disease APIs Configuration
These are the verified working API endpoints for each disease
Updated to support both API and CSV sources with comprehensive historical data (2010-2025)
"""

DISEASE_SOURCES = {
    # All diseases now use comprehensive CSV files (2010-2025, 30 districts, monthly data)
    # API is optional fallback for COVID-19 only
    "cholera": {
        "name": "Cholera",
        "type": "csv",
        "path": "data/cholera_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "covid19": {
        "name": "COVID-19",
        "type": "csv",
        "path": "data/covid19_pakistan_2010_2025.csv",
        "use_api": True,  # Optional API for validation/trends
        "api_url": "https://disease.sh/v3/covid-19/historical/Pakistan?lastdays=all",
    },
    "dengue": {
        "name": "Dengue",
        "type": "csv",
        "path": "data/dengue_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "hepatitis_a": {
        "name": "Hepatitis A",
        "type": "csv",
        "path": "data/hepatitis_a_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "influenza": {
        "name": "Influenza",
        "type": "csv",
        "path": "data/influenza_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "malaria": {
        "name": "Malaria",
        "type": "csv",
        "path": "data/malaria_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "pneumonia": {
        "name": "Pneumonia",
        "type": "csv",
        "path": "data/pneumonia_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "tuberculosis": {
        "name": "Tuberculosis",
        "type": "csv",
        "path": "data/tuberculosis_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
    "typhoid": {
        "name": "Typhoid",
        "type": "csv",
        "path": "data/typhoid_pakistan_2010_2025.csv",
        "use_api": False,
        "api_url": None,
    },
}

# Legacy support - map old names to new structure
WORKING_DISEASE_APIS = DISEASE_SOURCES
