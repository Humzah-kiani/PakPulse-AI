"""
Risk Index Calculator Module for PakPulse AI
Calculates Disease Risk Index (DRI) and Composite Health Risk Score
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

class RiskCalculator:
    """Class to calculate disease risk indices"""
    
    # Risk level thresholds
    RISK_LOW = 20
    RISK_MODERATE = 40
    RISK_HIGH = 60
    RISK_VERY_HIGH = 80
    RISK_CRITICAL = 100
    
    def __init__(self, use_weather: bool = True):
        """
        Initialize RiskCalculator
        
        Args:
            use_weather: Whether to incorporate weather data in risk calculations
        """
        self.use_weather = use_weather
        if use_weather:
            try:
                from src.weather_api import WeatherAPI
                self.weather_api = WeatherAPI()
            except ImportError:
                self.use_weather = False
                self.weather_api = None
        else:
            self.weather_api = None
    
    def calculate_dri(self, risk_index: float, disease: Optional[str] = None, 
                     lat: Optional[float] = None, lon: Optional[float] = None,
                     district: Optional[str] = None) -> Dict:
        """
        Calculate Disease Risk Index (DRI) classification
        Optionally adjusts risk based on weather conditions
        
        Args:
            risk_index: Risk index value (0-100)
            disease: Disease type (for weather adjustment)
            lat: Latitude (for weather data)
            lon: Longitude (for weather data)
            district: District name (for weather caching)
            
        Returns:
            Dictionary with DRI value, level, and description
        """
        # Get weather-adjusted risk if weather API is enabled
        adjusted_risk = float(risk_index)
        
        if self.use_weather and self.weather_api and disease and lat and lon:
            try:
                weather_data = self.weather_api.get_current_weather(lat, lon, district)
                weather_factor = self.weather_api.calculate_weather_risk_factor(weather_data, disease)
                
                # Apply weather factor (multiply base risk by factor)
                adjusted_risk = risk_index * weather_factor
            except Exception as e:
                print(f"Warning: Could not apply weather adjustment: {str(e)}")
                # Continue with original risk_index
        
        # Ensure risk_index is within valid range
        adjusted_risk = max(0, min(100, adjusted_risk))
        
        # Determine risk level
        if adjusted_risk <= self.RISK_LOW:
            level = "Low"
            description = "Minimal risk - Normal monitoring"
            color = "green"
        elif adjusted_risk <= self.RISK_MODERATE:
            level = "Moderate"
            description = "Elevated risk - Enhanced monitoring"
            color = "yellow"
        elif adjusted_risk <= self.RISK_HIGH:
            level = "High"
            description = "Significant risk - Active surveillance"
            color = "orange"
        elif adjusted_risk <= self.RISK_VERY_HIGH:
            level = "Very High"
            description = "Severe risk - Alert status"
            color = "red"
        else:
            level = "Critical"
            description = "Critical risk - Immediate action required"
            color = "darkred"
        
        result = {
            "dri": round(adjusted_risk, 2),
            "base_dri": round(risk_index, 2),
            "level": level,
            "description": description,
            "color": color
        }
        
        # Add weather info if used
        if self.use_weather and self.weather_api and disease and lat and lon:
            try:
                weather_data = self.weather_api.get_current_weather(lat, lon, district)
                result["weather_adjusted"] = True
                result["weather_factor"] = self.weather_api.calculate_weather_risk_factor(weather_data, disease)
                result["temperature"] = weather_data.get("temperature")
                result["humidity"] = weather_data.get("humidity")
            except:
                result["weather_adjusted"] = False
        else:
            result["weather_adjusted"] = False
        
        return result
    
    def calculate_composite_health_risk_score(self, district_data: pd.DataFrame) -> Dict:
        """
        Calculate Composite Health Risk Score for a district
        Combines multiple disease risks into a single vulnerability score
        
        Args:
            district_data: DataFrame with disease risk data for a district
                           Must have columns: 'disease', 'risk_index'
            
        Returns:
            Dictionary with composite score, breakdown, and recommendations
        """
        if district_data.empty:
            return {
                "composite_score": 0,
                "risk_level": "Low",
                "disease_count": 0,
                "breakdown": {},
                "recommendation": "No active disease risks"
            }
        
        # Get latest risk for each disease
        latest_data = district_data.groupby('disease')['risk_index'].max().reset_index()
        
        # Calculate weighted composite score
        # Higher weight for diseases with higher risk
        total_risk = 0
        disease_count = len(latest_data)
        breakdown = {}
        
        for _, row in latest_data.iterrows():
            disease = row['disease']
            risk = row['risk_index']
            
            # Weight: higher risk diseases contribute more
            weight = 1.0 + (risk / 100) * 0.5  # Weight between 1.0 and 1.5
            weighted_risk = risk * weight
            
            total_risk += weighted_risk
            breakdown[disease] = {
                "risk_index": round(risk, 2),
                "weight": round(weight, 2),
                "contribution": round(weighted_risk, 2)
            }
        
        # Average the weighted risks
        if disease_count > 0:
            composite_score = total_risk / disease_count
        else:
            composite_score = 0
        
        # Normalize to 0-100 range
        composite_score = min(100, max(0, composite_score))
        
        # Determine overall risk level
        dri_info = self.calculate_dri(composite_score)
        
        # Generate recommendation
        if composite_score >= self.RISK_VERY_HIGH:
            recommendation = "Immediate intervention required. Multiple high-risk diseases detected."
        elif composite_score >= self.RISK_HIGH:
            recommendation = "Enhanced surveillance and preventive measures recommended."
        elif composite_score >= self.RISK_MODERATE:
            recommendation = "Monitor closely and maintain standard preventive measures."
        else:
            recommendation = "Continue routine monitoring."
        
        return {
            "composite_score": round(composite_score, 2),
            "risk_level": dri_info["level"],
            "risk_description": dri_info["description"],
            "color": dri_info["color"],
            "disease_count": disease_count,
            "breakdown": breakdown,
            "recommendation": recommendation
        }
    
    def calculate_district_risk_summary(self, district_data: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive risk summary for a district
        
        Args:
            district_data: DataFrame with disease risk data for a district
            
        Returns:
            Dictionary with complete risk summary
        """
        if district_data.empty:
            return {
                "district": None,
                "composite_score": 0,
                "diseases": {},
                "highest_risk_disease": None,
                "trend": "stable"
            }
        
        district_name = district_data['district'].iloc[0] if 'district' in district_data.columns else None
        
        # Validate required columns
        if 'disease' not in district_data.columns:
            raise ValueError(f"Missing 'disease' column. Available columns: {list(district_data.columns)}")
        
        # Get latest data for each disease - use sort + first() to preserve grouping column
        sorted_data = district_data.sort_values('date', ascending=False)
        latest_data = sorted_data.groupby('disease', as_index=False).first()
        
        # Verify disease column is preserved
        if 'disease' not in latest_data.columns:
            # Fallback: use idxmax approach
            idx = district_data.groupby('disease')['date'].idxmax()
            latest_data = district_data.loc[idx].reset_index(drop=True)
        
        # Calculate DRI for each disease
        diseases_summary = {}
        highest_risk = 0
        highest_risk_disease = None
        
        for _, row in latest_data.iterrows():
            disease = row['disease']
            risk_index = row['risk_index']
            
            dri_info = self.calculate_dri(risk_index)
            diseases_summary[disease] = {
                "risk_index": round(risk_index, 2),
                "dri": dri_info,
                "date": row['date'].strftime('%Y-%m-%d') if 'date' in row else None
            }
            
            if risk_index > highest_risk:
                highest_risk = risk_index
                highest_risk_disease = disease
        
        # Calculate composite score
        composite = self.calculate_composite_health_risk_score(district_data)
        
        # Determine trend (simplified - compare latest vs previous)
        trend = "stable"
        if len(district_data) > 1:
            latest_avg = district_data.nlargest(2, 'date')['risk_index'].mean()
            previous_avg = district_data.nsmallest(2, 'date')['risk_index'].mean()
            if latest_avg > previous_avg * 1.1:
                trend = "increasing"
            elif latest_avg < previous_avg * 0.9:
                trend = "decreasing"
        
        return {
            "district": district_name,
            "composite_score": composite["composite_score"],
            "composite_level": composite["risk_level"],
            "diseases": diseases_summary,
            "highest_risk_disease": highest_risk_disease,
            "highest_risk_value": round(highest_risk, 2),
            "trend": trend,
            "recommendation": composite["recommendation"]
        }
    
    def get_risk_level_color(self, risk_index: float) -> str:
        """
        Get color code for risk level
        
        Args:
            risk_index: Risk index value (0-100)
            
        Returns:
            Color code (hex or name)
        """
        dri_info = self.calculate_dri(risk_index)
        return dri_info["color"]
    
    def get_risk_level_name(self, risk_index: float) -> str:
        """
        Get risk level name for risk index
        
        Args:
            risk_index: Risk index value (0-100)
            
        Returns:
            Risk level name
        """
        dri_info = self.calculate_dri(risk_index)
        return dri_info["level"]


# Convenience functions
def calculate_dri(risk_index: float) -> Dict:
    """Convenience function to calculate DRI"""
    calculator = RiskCalculator()
    return calculator.calculate_dri(risk_index)


def calculate_composite_score(district_data: pd.DataFrame) -> Dict:
    """Convenience function to calculate composite health risk score"""
    calculator = RiskCalculator()
    return calculator.calculate_composite_health_risk_score(district_data)

