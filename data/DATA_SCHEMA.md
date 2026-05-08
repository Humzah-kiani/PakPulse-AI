# Data Schema Documentation

## Overview
This document describes the data structure used in PakPulse AI for disease risk monitoring and visualization.

## Files

### 1. `disease_risk_data.csv` / `disease_risk_data.json`
Main dataset containing disease risk information for districts over time.

**Schema:**
- `district` (string): Name of the district
- `latitude` (float): Latitude coordinate of district center
- `longitude` (float): Longitude coordinate of district center
- `disease` (string): Disease type (dengue, malaria, cholera, influenza, covid19)
- `risk_index` (integer): Disease Risk Index (DRI) value from 0-100
  - 0-20: Low risk
  - 21-40: Moderate risk
  - 41-60: High risk
  - 61-80: Very high risk
  - 81-100: Critical risk
- `date` (string): Date in YYYY-MM-DD format
- `cases_reported` (integer): Number of reported cases (mock data)
- `population` (integer): District population (mock data)

**Example Record:**
```json
{
  "district": "Karachi",
  "latitude": 24.8607,
  "longitude": 67.0011,
  "disease": "dengue",
  "risk_index": 57,
  "date": "2025-08-08",
  "cases_reported": 430,
  "population": 2998796
}
```

### 2. `districts_metadata.csv` / `districts_metadata.json`
Metadata about districts including location and administrative information.

**Schema:**
- `district` (string): Name of the district
- `latitude` (float): Latitude coordinate of district center
- `longitude` (float): Longitude coordinate of district center
- `province` (string): Province name (Punjab, Sindh, Khyber Pakhtunkhwa, Balochistan, Federal)

**Example Record:**
```json
{
  "district": "Karachi",
  "latitude": 24.8607,
  "longitude": 67.0011,
  "province": "Sindh"
}
```

## Data Characteristics

### Districts Covered
- 20 major districts across Pakistan
- Includes major cities: Karachi, Lahore, Islamabad, Faisalabad, etc.
- Covers all major provinces

### Diseases Tracked
1. **Dengue** - Mosquito-borne viral disease
2. **Malaria** - Parasitic disease transmitted by mosquitoes
3. **Cholera** - Bacterial infection causing severe diarrhea
4. **Influenza** - Viral respiratory illness
5. **COVID-19** - Coronavirus disease

### Temporal Coverage
- Weekly data points
- Last 3 months (approximately 13 weeks)
- Date range: Varies based on generation date

### Risk Index Calculation (Mock Data)
The risk index is generated with realistic patterns:
- **Dengue**: Higher in urban areas (Karachi, Lahore) during monsoon season (July-September)
- **Malaria**: Higher in rural/agricultural areas during rainy season
- **Cholera**: Higher in areas with poor sanitation, especially in summer
- **Influenza**: Higher in winter months and densely populated areas
- **COVID-19**: Generally lower post-pandemic, slightly higher in major cities

## Usage Notes

- All data is **mock/sample data** for development and testing
- Risk indices are generated with realistic patterns but are not based on real health data
- Coordinates are approximate district centers
- Population and case numbers are randomly generated for demonstration

## Future Enhancements

When real data is integrated:
- Add data source attribution
- Include data quality indicators
- Add confidence intervals for risk indices
- Include historical trend data
- Add weather/climate correlation data

