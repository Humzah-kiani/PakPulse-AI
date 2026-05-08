"""
GIS Map Module for PakPulse AI
Simple map visualization with disease indicators
"""

import folium
from folium import plugins
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st
from streamlit_folium import st_folium
from src.data_loader import DataLoader
from src.risk_calculator import RiskCalculator

class GISMap:
    """Class to create and manage GIS maps"""
    
    def __init__(self):
        """Initialize GISMap"""
        self.loader = DataLoader()
        self.calculator = RiskCalculator()
        # Pakistan center coordinates
        self.pakistan_center = [30.3753, 69.3451]
        self.default_zoom = 6
    
    def get_risk_color(self, risk_index: float) -> str:
        """
        Get color based on risk index
        
        Args:
            risk_index: Risk index value (0-100)
            
        Returns:
            Hex color code
        """
        if risk_index <= 20:
            return '#10b981'  # Emerald - Low
        elif risk_index <= 40:
            return '#34d399'  # Medium Emerald - Moderate
        elif risk_index <= 60:
            return '#fbbf24'  # Amber - High
        elif risk_index <= 80:
            return '#f59e0b'  # Orange - Very High
        else:
            return '#ef4444'  # Red - Critical
    
    def create_base_map(self, zoom_start: Optional[int] = None) -> folium.Map:
        """
        Create base map of Pakistan
        
        Args:
            zoom_start: Initial zoom level
            
        Returns:
            Folium map object
        """
        zoom = zoom_start or self.default_zoom
        
        # Create map with OpenStreetMap tiles
        m = folium.Map(
            location=self.pakistan_center,
            zoom_start=zoom,
            tiles='OpenStreetMap',
            prefer_canvas=True
        )
        
        return m
    
    def add_district_markers(self, map_obj: folium.Map, 
                            disease_data: pd.DataFrame,
                            disease_filter: Optional[str] = None) -> folium.Map:
        """
        Add district markers to map based on disease risk with proper popups
        
        Args:
            map_obj: Folium map object
            disease_data: DataFrame with disease risk data
            disease_filter: Optional disease to filter by
            
        Returns:
            Updated map object
        """
        if disease_data.empty:
            return map_obj
        
        # Validate required columns
        required_columns = ['district', 'disease', 'date', 'latitude', 'longitude', 'risk_index']
        missing_columns = [col for col in required_columns if col not in disease_data.columns]
        if missing_columns:
            return map_obj
        
        # Filter by disease if specified
        if disease_filter:
            disease_data = disease_data[disease_data['disease'] == disease_filter].copy()
        
        if disease_data.empty:
            return map_obj
        
        # Get latest data for each district-disease combination
        sorted_data = disease_data.sort_values('date', ascending=False)
        latest_data = sorted_data.groupby(['district', 'disease'], as_index=False).first()
        
        # Verify columns are preserved
        if 'district' not in latest_data.columns or 'disease' not in latest_data.columns:
            idx = disease_data.groupby(['district', 'disease'])['date'].idxmax()
            latest_data = disease_data.loc[idx].reset_index(drop=True)
        
        # If filtering by single disease
        if disease_filter:
            for _, row in latest_data.iterrows():
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                risk = float(row['risk_index'])
                district = row['district']
                disease = row['disease']
                risk_level = self._get_risk_level(risk)
                
                risk_color = self.get_risk_color(risk)
                radius = 8 + (risk / 10)
                
                # Create detailed popup
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e293b;">{district}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px;"><b>Disease:</b></td><td style="padding: 5px;">{disease.title()}</td></tr>
                        <tr><td style="padding: 5px;"><b>Risk Score:</b></td><td style="padding: 5px;">{risk:.1f}</td></tr>
                        <tr><td style="padding: 5px;"><b>Risk Level:</b></td><td style="padding: 5px;">{risk_level}</td></tr>
                        <tr><td style="padding: 5px;"><b>Date:</b></td><td style="padding: 5px;">{row['date']}</td></tr>
                    </table>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{district} - {disease.title()}: Risk {risk:.1f}",
                    color=risk_color,
                    weight=2,
                    fillColor=risk_color,
                    fillOpacity=0.8,
                    opacity=1.0
                ).add_to(map_obj)
        else:
            # Show composite risk for all diseases
            for district in latest_data['district'].unique():
                district_data = latest_data[latest_data['district'] == district]
                
                lat = float(district_data.iloc[0]['latitude'])
                lon = float(district_data.iloc[0]['longitude'])
                
                # Calculate composite risk
                composite = self.calculator.calculate_composite_health_risk_score(district_data)
                risk_composite = composite['composite_score']
                risk_color = self.get_risk_color(risk_composite)
                risk_level = self._get_risk_level(risk_composite)
                radius = 8 + (risk_composite / 10)
                
                # Create popup showing all diseases in this district
                diseases_info = ""
                for _, disease_row in district_data.iterrows():
                    diseases_info += f"â€¢ {disease_row['disease'].title()}: {disease_row['risk_index']:.1f}<br>"
                
                popup_html = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e293b;">{district}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px;"><b>Composite Risk:</b></td><td style="padding: 5px;">{risk_composite:.1f}</td></tr>
                        <tr><td style="padding: 5px;"><b>Risk Level:</b></td><td style="padding: 5px;">{risk_level}</td></tr>
                        <tr><td style="padding: 5px;"><b>Diseases:</b></td><td style="padding: 5px;">{district_data.shape[0]}</td></tr>
                    </table>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                        <small>{diseases_info}</small>
                    </div>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{district} - Composite Risk: {risk_composite:.1f}",
                    color=risk_color,
                    weight=2,
                    fillColor=risk_color,
                    fillOpacity=0.8,
                    opacity=1.0
                ).add_to(map_obj)
        
        return map_obj
    
    def _get_risk_level(self, risk_index: float) -> str:
        """Get risk level text from risk index"""
        if risk_index <= 20:
            return "Low"
        elif risk_index <= 40:
            return "Moderate"
        elif risk_index <= 60:
            return "High"
        elif risk_index <= 80:
            return "Very High"
        else:
            return "Critical"
    
    def create_risk_heatmap(self, disease_data: pd.DataFrame,
                           disease_filter: Optional[str] = None,
                           date_filter: Optional[str] = None) -> folium.Map:
        """
        Create risk heatmap for disease data with disease indicators
        
        Args:
            disease_data: DataFrame with disease risk data
            disease_filter: Optional disease to filter by
            date_filter: Optional date to filter by (YYYY-MM-DD)
            
        Returns:
            Folium map with disease markers
        """
        # Create base map with light tiles for better visibility
        m = self.create_base_map()
        
        # Validate required columns
        required_columns = ['district', 'disease', 'date', 'latitude', 'longitude', 'risk_index']
        if disease_data.empty:
            return m  # Return empty map if no data
        
        missing_columns = [col for col in required_columns if col not in disease_data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in data: {missing_columns}. "
                           f"Available columns: {list(disease_data.columns)}")
        
        # Apply filters
        filtered_data = disease_data.copy()
        if disease_filter:
            filtered_data = filtered_data[filtered_data['disease'] == disease_filter]
        
        if date_filter:
            try:
                date_obj = pd.to_datetime(date_filter)
                filtered_data = filtered_data[filtered_data['date'] == date_obj]
            except:
                pass  # If date filter fails, use all data
        
        # Get latest data for each district-disease combination
        if filtered_data.empty:
            # If no data after filtering, use all data
            filtered_data = disease_data.copy()
            if disease_filter:
                filtered_data = filtered_data[filtered_data['disease'] == disease_filter]
        
        if filtered_data.empty:
            return m  # Return empty map if no data after filtering
        
        # Use sort + first() method to preserve all columns
        sorted_data = filtered_data.sort_values('date', ascending=False)
        latest_data = sorted_data.groupby(['district', 'disease'], as_index=False).first()
        
        # Verify columns are preserved
        if 'district' not in latest_data.columns or 'disease' not in latest_data.columns:
            # Fallback: use idxmax approach
            idx = filtered_data.groupby(['district', 'disease'])['date'].idxmax()
            latest_data = filtered_data.loc[idx].reset_index(drop=True)
        
        # Prepare heatmap data with proper weighting
        heat_data = []
        max_risk = latest_data['risk_index'].max() if not latest_data.empty else 100
        min_risk = latest_data['risk_index'].min() if not latest_data.empty else 0
        
        for _, row in latest_data.iterrows():
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            risk = float(row['risk_index'])
            
            # Normalize risk to 0-1 scale for heatmap intensity
            if max_risk > min_risk:
                weight = (risk - min_risk) / (max_risk - min_risk)
            else:
                weight = 0.5
            
            # Ensure weight is between 0.1 and 1.0
            weight = min(1.0, max(0.1, weight))
            heat_data.append([lat, lon, weight])
        
        # Add heatmap layer with improved gradient
        if heat_data and len(heat_data) > 0:
            try:
                plugins.HeatMap(
                    heat_data,
                    name='Disease Risk Hotspots',
                    min_opacity=0.3,
                    max_zoom=18,
                    radius=50,
                    blur=25,
                    max_intensity=1.0,
                    gradient={
                        0.0: '#1e40af',   # Dark Blue - low risk
                        0.2: '#0084ff',   # Blue
                        0.4: '#00ff00',   # Green
                        0.6: '#ffff00',   # Yellow
                        0.8: '#ff8800',   # Orange
                        1.0: '#ff0000'    # Red - critical hotspot
                    }
                ).add_to(m)
            except Exception as e:
                print(f"Warning: Heatmap layer: {str(e)}")
        
        # Add circle markers on top of heatmap for precise location and detailed info
        for _, row in latest_data.iterrows():
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            risk = float(row['risk_index'])
            district = row['district']
            disease = row['disease']
            
            color = self.get_risk_color(risk)
            risk_level = self._get_risk_level(risk)
            
            # Circle marker size based on risk (8-20 radius range)
            radius = 8 + min(12, risk / 10)
            
            # Detailed popup with disease and risk information
            popup_html = f"""
            <div style="font-family: Arial; width: 220px; padding: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #1e293b; border-bottom: 2px solid {color}; padding-bottom: 8px;">{district}</h4>
                <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 6px; font-weight: bold; color: #475569;">Disease:</td>
                        <td style="padding: 6px; color: #1e293b;">{disease.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; font-weight: bold; color: #475569;">Risk Score:</td>
                        <td style="padding: 6px; color: #1e293b; font-weight: bold;">{risk:.1f}/100</td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 6px; font-weight: bold; color: #475569;">Risk Level:</td>
                        <td style="padding: 6px; color: {color}; font-weight: bold;">{risk_level}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; font-weight: bold; color: #475569;">Date:</td>
                        <td style="padding: 6px; color: #1e293b;">{row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])[:10]}</td>
                    </tr>
                </table>
                <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #e2e8f0;">
                    <div style="color: #64748b; font-size: 11px;">
                        <b>Hotspot Indicator:</b> {('ðŸ”´ Critical Hotspot' if risk >= 80 else 'ðŸŸ  High Risk Area' if risk >= 60 else 'ðŸŸ¡ Moderate Area' if risk >= 40 else 'ðŸŸ¢ Low Risk')}
                    </div>
                </div>
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"<b>{district}</b><br>{disease.title()}: {risk:.1f} ({risk_level})",
                color=color,
                weight=2.5,
                fillColor=color,
                fillOpacity=0.85,
                opacity=1.0
            ).add_to(m)
        
        return m
    
    def create_multi_disease_map(self, disease_data: pd.DataFrame,
                                 selected_diseases: List[str],
                                 map_view: str = 'Light Map') -> folium.Map:
        """
        Create map with multiple disease layers
        
        Args:
            disease_data: DataFrame with disease risk data
            selected_diseases: List of diseases to display
            map_view: Type of map view to use
            
        Returns:
            Folium map with multiple disease layers
        """
        m = self.create_base_map(map_view=map_view)
        
        # Validate required columns
        if disease_data.empty:
            return m
        
        required_columns = ['district', 'disease', 'date', 'latitude', 'longitude', 'risk_index']
        missing_columns = [col for col in required_columns if col not in disease_data.columns]
        if missing_columns:
            return m  # Return empty map if columns are missing
        
        # Color scheme for different diseases
        disease_colors = {
            'covid19': '#FF9800',      # Orange
            'dengue': '#E91E63',        # Pink
            'influenza': '#2196F3',     # Blue
            'malaria': '#9C27B0',       # Purple
            'cholera': '#F44336',       # Red
            'pneumonia': '#00BCD4',     # Cyan
            'tuberculosis': '#795548',   # Brown
            'typhoid': '#FF5722',        # Deep Orange
            'hepatitis_a': '#4CAF50'     # Green
        }
        
        # Get latest data - use a method that preserves grouping columns
        try:
            # Check if grouping columns exist
            if 'district' not in disease_data.columns or 'disease' not in disease_data.columns:
                raise ValueError(f"Missing required columns for grouping. Available columns: {list(disease_data.columns)}")
            
            # Method 1: Sort by date and use groupby().first() - this preserves all columns
            # Sort by date descending to get latest first
            sorted_data = disease_data.sort_values('date', ascending=False)
            
            # Group by district and disease, take first (latest) row
            # This preserves all columns including district and disease
            latest_data = sorted_data.groupby(['district', 'disease'], as_index=False).first()
            
            # Alternative method if the above doesn't work: use idxmax and iloc
            # Verify columns are present
            if 'district' not in latest_data.columns or 'disease' not in latest_data.columns:
                # Fallback: use idxmax approach but preserve columns manually
                idx = disease_data.groupby(['district', 'disease'])['date'].idxmax()
                latest_data = disease_data.loc[idx].reset_index(drop=True)
                
        except KeyError as e:
            raise ValueError(f"Missing required column for grouping: {str(e)}. Available columns: {list(disease_data.columns)}")
        
        # Filter by selected diseases
        if latest_data.empty:
            return m  # Return empty map if no data after grouping
        
        try:
            filtered_data = latest_data[latest_data['disease'].isin(selected_diseases)]
        except KeyError:
            raise ValueError(f"Missing 'disease' column. Available columns: {list(latest_data.columns)}")
        
        if filtered_data.empty:
            return m  # Return empty map if no data for selected diseases
        
        # Add markers for each disease with better visualization
        for disease in selected_diseases:
            disease_data_filtered = filtered_data[filtered_data['disease'] == disease]
            if disease_data_filtered.empty:
                continue  # Skip if no data for this disease
            
            # Use risk-based coloring instead of disease-specific color
            for _, row in disease_data_filtered.iterrows():
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                risk = float(row['risk_index'])
                district = row['district']
                risk_level = self._get_risk_level(risk)
                
                # Use risk-based color
                color = self.get_risk_color(risk)
                radius = 8 + (risk / 10)
                
                # Create popup with disease information
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e293b;">{district}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px;"><b>Disease:</b></td><td style="padding: 5px;">{disease.title()}</td></tr>
                        <tr><td style="padding: 5px;"><b>Risk Score:</b></td><td style="padding: 5px;">{risk:.1f}</td></tr>
                        <tr><td style="padding: 5px;"><b>Risk Level:</b></td><td style="padding: 5px;">{risk_level}</td></tr>
                        <tr><td style="padding: 5px;"><b>Date:</b></td><td style="padding: 5px;">{row['date']}</td></tr>
                    </table>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{district} - {disease.title()}: Risk {risk:.1f}",
                    color=color,
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.8,
                    opacity=1.0
                ).add_to(m)
        
        # Return map without legend to avoid JSON serialization issues
        return m
    
    def add_risk_legend(self, map_obj: folium.Map) -> folium.Map:
        """
        Add professional risk level legend to map
        
        Args:
            map_obj: Folium map object
            
        Returns:
            Updated map object
        """
        legend_html = '''
        <div style="
            position: fixed; 
            bottom: 50px; left: 50px; 
            width: 180px; 
            background-color: white; 
            border: 3px solid #1e293b; 
            z-index: 9999; 
            font-size: 13px;
            font-family: Arial, sans-serif;
            padding: 12px; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            color: #000000 !important;
        ">
            <div style="
                background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
                color: #000000 !important;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 10px;
                font-weight: bold;
                text-align: center;
                border: 1px solid #94a3b8;
            ">
                DISEASE RISK LEVELS
            </div>
            
            <div style="padding: 5px; margin: 5px 0; color: #000000 !important;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="
                        width: 16px; height: 16px; 
                        background-color: #ef4444; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid #dc2626;
                    "></div>
                    <span style="color: #000000 !important;"><b>Critical</b> (80+)</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="
                        width: 16px; height: 16px; 
                        background-color: #f59e0b; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid #d97706;
                    "></div>
                    <span style="color: #000000 !important;"><b>Very High</b> (60-80)</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="
                        width: 16px; height: 16px; 
                        background-color: #fbbf24; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid #d97706;
                    "></div>
                    <span style="color: #000000 !important;"><b>High</b> (40-60)</span>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="
                        width: 16px; height: 16px; 
                        background-color: #34d399; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid #10b981;
                    "></div>
                    <span style="color: #000000 !important;"><b>Moderate</b> (20-40)</span>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <div style="
                        width: 16px; height: 16px; 
                        background-color: #10b981; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid #059669;
                    "></div>
                    <span style="color: #000000 !important;"><b>Low</b> (0-20)</span>
                </div>
            </div>
            
            <div style="
                margin-top: 10px;
                padding-top: 10px;
                border-top: 2px solid #e2e8f0;
                font-size: 11px;
                color: #000000 !important;
                text-align: center;
            ">
                Circle size indicates risk intensity
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        return map_obj
    
    def add_disease_legend(self, map_obj: folium.Map, diseases: List[str]) -> folium.Map:
        """
        Add disease information legend to map
        
        Args:
            map_obj: Folium map object
            diseases: List of diseases displayed
            
        Returns:
            Updated map object
        """
        disease_list_html = ""
        for disease in diseases:
            disease_list_html += f"<div style=\"padding: 3px; margin: 3px 0;\">â€¢ {disease.title()}</div>"
        
        legend_html = f'''
        <div style="
            position: fixed; 
            bottom: 50px; right: 50px; 
            width: 180px; 
            background-color: white; 
            border: 3px solid #1e293b; 
            z-index: 9999; 
            font-size: 12px;
            font-family: Arial, sans-serif;
            padding: 12px; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            color: #000000 !important;
        ">
            <div style="
                background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
                color: #000000 !important;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 10px;
                font-weight: bold;
                text-align: center;
                font-size: 13px;
                border: 1px solid #94a3b8;
            ">
                DISEASES SHOWN
            </div>
            
            <div style="max-height: 200px; overflow-y: auto; color: #000000 !important;">
                {disease_list_html}
            </div>
            
            <div style="
                margin-top: 10px;
                padding-top: 10px;
                border-top: 2px solid #e2e8f0;
                font-size: 10px;
                color: #000000 !important;
                text-align: center;
            ">
                Color by Risk Level
            </div>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        return map_obj


# Convenience functions
def create_base_map(zoom_start: Optional[int] = None) -> folium.Map:
    """Convenience function to create base map"""
    gis = GISMap()
    return gis.create_base_map(zoom_start)

