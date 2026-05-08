# Data Loading Module

## Overview

The `data_loader.py` module provides functionality to load and extract disease risk data and district metadata from CSV/JSON files.

## Location

**Data Loading Module:** `src/data_loader.py`

**Data Files Location:** `data/` directory
- `data/disease_risk_data.csv` - Main disease risk dataset
- `data/disease_risk_data.json` - Same data in JSON format
- `data/districts_metadata.csv` - District coordinates and metadata
- `data/districts_metadata.json` - Same metadata in JSON format

## Usage

### Basic Usage

```python
from src.data_loader import DataLoader, load_disease_data, load_districts_metadata

# Method 1: Using DataLoader class
loader = DataLoader()
disease_data = loader.load_disease_data()  # Loads CSV by default
districts = loader.load_districts_metadata()

# Method 2: Using convenience functions
disease_data = load_disease_data()  # Loads from CSV
districts = load_districts_metadata()  # Loads from CSV
```

### Filtering Data

```python
loader = DataLoader()

# Get data for specific district
karachi_data = loader.get_disease_data_by_district("Karachi")

# Get data for specific disease
dengue_data = loader.get_disease_data_by_disease("dengue")

# Get data by date range
recent_data = loader.get_disease_data_by_date_range("2025-10-01", "2025-10-31")

# Get latest risk data
latest = loader.get_latest_risk_data()
```

### Getting Metadata

```python
loader = DataLoader()

# Get district coordinates
lat, lon = loader.get_district_coordinates("Lahore")

# Get all districts
all_districts = loader.get_all_districts()

# Get all diseases
all_diseases = loader.get_all_diseases()

# Get risk summary for a district
summary = loader.get_district_risk_summary("Karachi")
```

## Integration with Streamlit

In your Streamlit app (`app.py`), you can use the data loader like this:

```python
import streamlit as st
from src.data_loader import DataLoader

# Initialize loader (cached for performance)
@st.cache_data
def load_data():
    loader = DataLoader()
    return loader.load_disease_data()

# Use in your app
disease_data = load_data()
st.dataframe(disease_data)
```

## Data Structure

See `data/DATA_SCHEMA.md` for detailed information about the data structure and fields.

