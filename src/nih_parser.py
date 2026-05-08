"""
NIH Pakistan Weekly Epidemiological Report Parser
Extracts district-wise disease data from NIH PDF reports
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

def load_nih_weekly_report(pdf_path: str) -> pd.DataFrame:
    """
    Extract district-wise disease data from NIH Weekly Epidemiological Report PDF
    
    Args:
        pdf_path: Path to PDF file (e.g., "data/WER_Week45.pdf")
        
    Returns:
        DataFrame with columns: ["district", "disease", "cases", "week"]
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    all_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract week number from filename or content
            week_match = re.search(r'Week\s*(\d+)', pdf_path.stem, re.IGNORECASE)
            week = week_match.group(1) if week_match else "Unknown"
            
            # Try to extract year from filename or content
            year_match = re.search(r'(\d{4})', pdf_path.stem)
            year = year_match.group(1) if year_match else str(datetime.now().year)
            
            # Process each page
            for page_num, page in enumerate(pdf.pages):
                # Extract tables from page
                tables = page.extract_tables()
                
                if not tables:
                    continue
                
                # Process each table
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Try to identify table structure
                    # Look for district names and disease data
                    processed_data = _parse_table(table, week, year)
                    all_data.extend(processed_data)
        
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            # Clean and standardize data
            df = _clean_nih_data(df)
            return df
        else:
            print(f"Warning: No data extracted from {pdf_path}")
            return pd.DataFrame(columns=["district", "disease", "cases", "week"])
            
    except Exception as e:
        print(f"Error parsing PDF {pdf_path}: {str(e)}")
        return pd.DataFrame(columns=["district", "disease", "cases", "week"])

def _parse_table(table: List[List], week: str, year: str) -> List[Dict]:
    """
    Parse a table to extract district and disease data
    
    Args:
        table: Table data from PDF
        week: Week number
        year: Year
        
    Returns:
        List of dictionaries with district, disease, cases, week
    """
    data = []
    
    if not table or len(table) < 2:
        return data
    
    # Try to identify header row
    header_row = None
    for i, row in enumerate(table[:5]):  # Check first 5 rows
        if row and any(cell and isinstance(cell, str) and 
                      ('district' in cell.lower() or 'disease' in cell.lower() or 
                       'cases' in cell.lower() or 'location' in cell.lower()) 
                      for cell in row):
            header_row = i
            break
    
    if header_row is None:
        header_row = 0
    
    # Common disease names to look for
    disease_keywords = ['dengue', 'malaria', 'cholera', 'influenza', 'covid', 
                       'diarrhea', 'typhoid', 'measles', 'hepatitis']
    
    # Process rows
    for row_idx in range(header_row + 1, len(table)):
        row = table[row_idx]
        if not row or len(row) < 2:
            continue
        
        # Try to extract district name (usually first column)
        district = None
        if row[0] and isinstance(row[0], str):
            district = row[0].strip()
            # Skip header-like rows
            if any(keyword in district.lower() for keyword in ['total', 'sum', 'district', 'location', '']):
                continue
        
        # Look for disease and cases in remaining columns
        for col_idx in range(1, len(row)):
            cell = row[col_idx]
            if not cell:
                continue
            
            cell_str = str(cell).strip()
            
            # Check if this column contains disease name
            disease = None
            for keyword in disease_keywords:
                if keyword in cell_str.lower():
                    disease = keyword
                    break
            
            # If no disease found, try to extract numeric value (cases)
            if not disease and cell_str.replace(',', '').replace('.', '').isdigit():
                cases = int(float(cell_str.replace(',', '')))
                # Try to infer disease from column header or previous context
                if col_idx > 0 and row[header_row] and isinstance(row[header_row], str):
                    header = row[header_row].lower()
                    for keyword in disease_keywords:
                        if keyword in header:
                            disease = keyword
                            break
                
                # If we have district and cases, add to data
                if district and cases > 0:
                    data.append({
                        "district": district,
                        "disease": disease or "unknown",
                        "cases": cases,
                        "week": f"{year}-W{week}"
                    })
    
    return data

def _clean_nih_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize NIH data
    
    Args:
        df: Raw DataFrame from PDF parsing
        
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    # Remove rows with missing essential data
    df = df.dropna(subset=['district', 'cases'])
    
    # Clean district names
    df['district'] = df['district'].str.strip()
    df['district'] = df['district'].str.title()
    
    # Standardize disease names
    disease_mapping = {
        'dengue': 'dengue',
        'malaria': 'malaria',
        'cholera': 'cholera',
        'influenza': 'influenza',
        'flu': 'influenza',
        'covid': 'covid19',
        'covid-19': 'covid19',
        'covid19': 'covid19'
    }
    
    df['disease'] = df['disease'].str.lower().str.strip()
    df['disease'] = df['disease'].map(disease_mapping).fillna(df['disease'])
    
    # Ensure cases is numeric
    df['cases'] = pd.to_numeric(df['cases'], errors='coerce')
    df = df.dropna(subset=['cases'])
    df['cases'] = df['cases'].astype(int)
    
    # Remove rows with zero cases
    df = df[df['cases'] > 0]
    
    return df.reset_index(drop=True)

def find_latest_nih_report(data_dir: str = "data") -> Optional[Path]:
    """
    Find the latest NIH weekly report PDF in data directory
    
    Args:
        data_dir: Directory to search
        
    Returns:
        Path to latest PDF or None
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return None
    
    # Look for PDF files with WER or Week in name
    pdf_files = list(data_path.glob("**/*WER*.pdf")) + list(data_path.glob("**/*Week*.pdf"))
    
    if not pdf_files:
        return None
    
    # Sort by modification time, return latest
    pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return pdf_files[0]




