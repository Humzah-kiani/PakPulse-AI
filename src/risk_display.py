"""
Risk Index Display Components for PakPulse AI
Streamlit UI components for displaying disease risk indices and scores
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from src.risk_calculator import RiskCalculator

class RiskDisplay:
    """Class to create Streamlit display components for risk indices"""
    
    def __init__(self):
        """Initialize RiskDisplay"""
        self.calculator = RiskCalculator()
    
    def display_dri_card(self, disease: str, risk_index: float, 
                         show_description: bool = True) -> None:
        """
        Display a Disease Risk Index (DRI) card with visual indicators
        
        Args:
            disease: Disease name
            risk_index: Risk index value (0-100)
            show_description: Whether to show risk description
        """
        dri_info = self.calculator.calculate_dri(risk_index)
        
        # Color mapping for professional display
        color_map = {
            "green": "#4CAF50",
            "yellow": "#FFC107",
            "orange": "#FF9800",
            "red": "#F44336",
            "darkred": "#B71C1C"
        }
        
        color = color_map.get(dri_info["color"], "#9E9E9E")
        
        # Create columns for layout
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.markdown(f"**{disease.upper()}**")
            st.markdown(f"<span style='color: {color}; font-weight: 600;'>â—</span> **{dri_info['level']}**", unsafe_allow_html=True)
        
        with col2:
            # Progress bar
            st.progress(risk_index / 100)
            st.caption(f"DRI: {dri_info['dri']}/100")
        
        with col3:
            st.metric("Risk", dri_info['dri'], delta=None)
        
        if show_description:
            st.info(f"{dri_info['description']}")
    
    def display_composite_score_card(self, composite_data: Dict) -> None:
        """
        Display Composite Health Risk Score card with professional styling
        
        Args:
            composite_data: Dictionary from calculate_composite_health_risk_score()
        """
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Composite Health Risk Score</h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Score with color coding - Professional Card
            score = composite_data['composite_score']
            level = composite_data['risk_level']
            
            # Color based on risk level
            if score <= 20:
                color = "#10B981"
                bg_color = "#D1FAE5"
                color_name = "Low"
            elif score <= 40:
                color = "#F59E0B"
                bg_color = "#FEF3C7"
                color_name = "Moderate"
            elif score <= 60:
                color = "#F97316"
                bg_color = "#FED7AA"
                color_name = "High"
            elif score <= 80:
                color = "#EF4444"
                bg_color = "#FEE2E2"
                color_name = "Very High"
            else:
                color = "#B91C1C"
                bg_color = "#FECACA"
                color_name = "Critical"
            
            st.markdown(f"""
            <div style="
                background: {bg_color};
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            ">
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Composite Score</div>
                <div style="color: {color}; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">{score:.1f}<span style="font-size: 1.5rem; color: #64748b;">/100</span></div>
                <div style="color: #1e293b; font-size: 1rem; font-weight: 600;">{level} Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #f8fafc;
                border-radius: 8px;
                padding: 1.5rem;
                border: 1px solid #e2e8f0;
            ">
            """, unsafe_allow_html=True)
            st.metric("Active Diseases", composite_data['disease_count'])
            st.caption("Diseases with active risk")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: #f8fafc;
                border-radius: 8px;
                padding: 1.5rem;
                border: 1px solid #e2e8f0;
            ">
            """, unsafe_allow_html=True)
            # Progress visualization
            st.progress(score / 100)
            st.caption(f"Overall Vulnerability")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Recommendation - Professional Styling
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 1.25rem;
            margin-top: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        ">
            <div style="color: #1e293b; font-size: 0.9375rem; line-height: 1.6;">
                <strong style="color: #0f172a;">Recommendation:</strong> {composite_data['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Breakdown by disease
        if composite_data['breakdown']:
            with st.expander("Risk Breakdown by Disease"):
                breakdown_df = pd.DataFrame([
                    {
                        'Disease': disease,
                        'Risk Index': data['risk_index'],
                        'Contribution': f"{data['contribution']:.1f}"
                    }
                    for disease, data in composite_data['breakdown'].items()
                ])
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    
    def display_district_risk_summary(self, summary: Dict) -> None:
        """
        Display comprehensive district risk summary with professional layout
        
        Args:
            summary: Dictionary from calculate_district_risk_summary()
        """
        if not summary or summary.get('district') is None:
            st.warning("No risk data available for this district")
            return
        
        st.markdown(f"## {summary['district']} - Risk Summary")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Composite Score", f"{summary['composite_score']:.1f}", 
                     summary['composite_level'])
        
        with col2:
            highest_disease = summary.get('highest_risk_disease', 'N/A')
            highest_value = summary.get('highest_risk_value', 0)
            st.metric("Highest Risk", highest_disease, f"{highest_value:.1f}")
        
        with col3:
            disease_count = len(summary.get('diseases', {}))
            st.metric("Active Diseases", disease_count)
        
        with col4:
            trend = summary.get('trend', 'stable')
            trend_symbol = "â†‘" if trend == "increasing" else "â†“" if trend == "decreasing" else "â†’"
            st.metric("Trend", f"{trend_symbol} {trend.title()}")
        
        # Recommendation
        if summary.get('recommendation'):
            st.info(f"**Recommendation:** {summary['recommendation']}")
        
        # Disease breakdown - Professional grid layout
        st.markdown("### Disease Risk Breakdown")
        diseases_data = summary.get('diseases', {})
        
        if diseases_data:
            # Sort diseases by risk index (highest first)
            sorted_diseases = sorted(
                diseases_data.items(), 
                key=lambda x: x[1].get('risk_index', 0), 
                reverse=True
            )
            
            # Use a fixed grid layout (4 columns) for better visual organization
            num_cols = 4
            num_diseases = len(sorted_diseases)
            
            # Create rows dynamically
            for row_start in range(0, num_diseases, num_cols):
                cols = st.columns(num_cols)
                row_diseases = sorted_diseases[row_start:row_start + num_cols]
                
                for col_idx, (disease, data) in enumerate(row_diseases):
                    with cols[col_idx]:
                        self.display_disease_risk_card(disease, data.get('risk_index', 0))
    
    def display_risk_chart(self, data: pd.DataFrame, 
                          chart_type: str = "bar") -> None:
        """
        Display risk visualization chart
        
        Args:
            data: DataFrame with risk data (must have 'disease' and 'risk_index' columns)
            chart_type: Type of chart ('bar', 'line', 'scatter')
        """
        if data.empty:
            st.warning("No data available for chart")
            return
        
        if chart_type == "bar":
            # Create professional bar chart with enhanced styling
            fig = px.bar(
                data,
                x='disease',
                y='risk_index',
                color='risk_index',
                color_continuous_scale=[
                    [0, '#10B981'],      # Green for low risk
                    [0.2, '#F59E0B'],    # Amber for moderate
                    [0.4, '#F97316'],    # Orange for high
                    [0.6, '#EF4444'],    # Red for very high
                    [1.0, '#B91C1C']     # Dark red for critical
                ],
                title="<b>Disease Risk Index Comparison</b>",
                labels={
                    'risk_index': '<b>Risk Index</b>', 
                    'disease': '<b>Disease</b>'
                },
                text='risk_index'
            )
            
            # Enhanced bar chart styling
            fig.update_traces(
                texttemplate='%{text:.1f}',
                textposition='outside',
                marker=dict(
                    line=dict(width=0.5, color='white'),
                    opacity=0.9
                ),
                hovertemplate='<b>%{x}</b><br>Risk Index: %{y:.2f}<extra></extra>'
            )
            
            # Professional layout
            fig.update_layout(
                height=450,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Arial, sans-serif', size=12, color='#1e293b'),
                title=dict(
                    font=dict(size=18, color='#1e293b', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title_font=dict(size=13, color='#475569'),
                    tickfont=dict(size=10, color='#64748b'),
                    gridcolor='#f1f5f9',
                    showgrid=True,
                    gridwidth=1
                ),
                yaxis=dict(
                    title_font=dict(size=13, color='#475569'),
                    tickfont=dict(size=11, color='#64748b'),
                    gridcolor='#e2e8f0',
                    showgrid=True,
                    gridwidth=1,
                    zeroline=False
                ),
                margin=dict(l=10, r=10, t=50, b=50)
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=-45)
        
        elif chart_type == "line":
            if 'date' in data.columns:
                fig = px.line(
                    data,
                    x='date',
                    y='risk_index',
                    color='disease',
                    title="Risk Index Trend Over Time",
                    labels={'risk_index': 'Risk Index', 'date': 'Date'}
                )
                fig.update_layout(height=400)
            else:
                st.warning("Date column required for line chart")
                return
        
        else:  # scatter
            fig = px.scatter(
                data,
                x='disease',
                y='risk_index',
                size='risk_index',
                color='risk_index',
                color_continuous_scale='RdYlGn_r',
                title="Risk Index Scatter Plot",
                labels={'risk_index': 'Risk Index', 'disease': 'Disease'}
            )
            fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_risk_gauge(self, risk_index: float, title: str = "Risk Index") -> None:
        """
        Display risk index as a professional gauge chart with enhanced styling
        
        Args:
            risk_index: Risk index value (0-100)
            title: Chart title
        """
        # Get risk level information
        dri_info = self.calculator.calculate_dri(risk_index)
        
        # Professional color scheme
        if risk_index <= 20:
            bar_color = "#10B981"  # Emerald green
            level_color = "#059669"
            level_name = "Low"
        elif risk_index <= 40:
            bar_color = "#F59E0B"  # Amber
            level_color = "#D97706"
            level_name = "Moderate"
        elif risk_index <= 60:
            bar_color = "#F97316"  # Orange
            level_color = "#EA580C"
            level_name = "High"
        elif risk_index <= 80:
            bar_color = "#EF4444"  # Red
            level_color = "#DC2626"
            level_name = "Very High"
        else:
            bar_color = "#B91C1C"  # Dark red
            level_color = "#991B1B"
            level_name = "Critical"
        
        # Create professional gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_index,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{title}</b>",
                'font': {'size': 18, 'color': '#1e293b', 'family': 'Arial, sans-serif'}
            },
            number = {
                'font': {'size': 42, 'color': bar_color, 'family': 'Arial, sans-serif'},
                'suffix': '',
                'valueformat': '.1f'
            },
            gauge = {
                'axis': {
                    'range': [None, 100],
                    'tickwidth': 1,
                    'tickcolor': "#64748b",
                    'tickfont': {'size': 11, 'color': '#64748b'},
                    'tickmode': 'linear',
                    'tick0': 0,
                    'dtick': 20
                },
                'bar': {
                    'color': bar_color,
                    'thickness': 0.15,
                    'line': {'width': 0}
                },
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e2e8f0",
                'steps': [
                    {'range': [0, 20], 'color': "#D1FAE5"},      # Very light green
                    {'range': [20, 40], 'color': "#FEF3C7"},     # Very light yellow
                    {'range': [40, 60], 'color': "#FED7AA"},     # Very light orange
                    {'range': [60, 80], 'color': "#FEE2E2"},     # Very light red
                    {'range': [80, 100], 'color': "#FECACA"}     # Light red
                ],
                'threshold': {
                    'line': {'color': bar_color, 'width': 3},
                    'thickness': 0.75,
                    'value': risk_index
                }
            }
        ))
        
        # Enhanced layout with professional styling
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family="Arial, sans-serif", color="#1e293b")
        )
        
        # Display the gauge
        st.plotly_chart(fig, use_container_width=True)
        
        # Add professional risk level badge below the gauge
        risk_level_html = f"""
        <div style="
            text-align: center;
            margin-top: -20px;
            margin-bottom: 10px;
        ">
            <span style="
                display: inline-block;
                background: linear-gradient(135deg, {bar_color} 0%, {level_color} 100%);
                color: white;
                padding: 0.5rem 1.5rem;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                letter-spacing: 0.5px;
            ">{level_name} Risk</span>
        </div>
        """
        st.markdown(risk_level_html, unsafe_allow_html=True)
    
    def display_risk_table(self, data: pd.DataFrame) -> None:
        """
        Display risk data in a formatted table
        
        Args:
            data: DataFrame with risk data
        """
        if data.empty:
            st.warning("No data available")
            return
        
        # Format the dataframe for display
        display_df = data.copy()
        
        # Add risk level column
        if 'risk_index' in display_df.columns:
            display_df['Risk Level'] = display_df['risk_index'].apply(
                lambda x: self.calculator.get_risk_level_name(x)
            )
            display_df['Risk Index'] = display_df['risk_index'].round(2)
            display_df = display_df.drop(columns=['risk_index'])
        
        # Reorder columns for better display
        priority_cols = ['district', 'disease', 'Risk Index', 'Risk Level', 'date']
        other_cols = [col for col in display_df.columns if col not in priority_cols]
        column_order = [col for col in priority_cols if col in display_df.columns] + other_cols
        
        display_df = display_df[column_order]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    def display_risk_heatmap_dataframe(self, data: pd.DataFrame) -> None:
        """
        Display risk data as a heatmap-style dataframe
        
        Args:
            data: DataFrame with columns: district, disease, risk_index
        """
        if data.empty or 'district' not in data.columns or 'disease' not in data.columns:
            st.warning("Data must contain 'district' and 'disease' columns")
            return
        
        # Pivot table: districts as rows, diseases as columns
        pivot_df = data.pivot_table(
            values='risk_index',
            index='district',
            columns='disease',
            aggfunc='mean'
        ).round(1)
        
        # Style the dataframe with color coding
        def color_risk(val):
            if val <= 20:
                return 'background-color: #90EE90'  # Light green
            elif val <= 40:
                return 'background-color: #FFFFE0'  # Light yellow
            elif val <= 60:
                return 'background-color: #FFA500'  # Orange
            elif val <= 80:
                return 'background-color: #FF6B6B'  # Light red
            else:
                return 'background-color: #DC143C'  # Crimson
        
        styled_df = pivot_df.style.applymap(color_risk)
        st.dataframe(styled_df, use_container_width=True, height=400)
    
    def display_disease_risk_card(self, disease: str, risk_index: float) -> None:
        """
        Display a compact, professional disease risk card
        
        Args:
            disease: Disease name
            risk_index: Risk index value (0-100 or 0-1 scale)
        """
        # Normalize risk_index to 0-100 scale if it's on 0-1 scale
        # Check if risk_index is likely on 0-1 scale (values <= 1.0 and > 0)
        normalized_risk_index = risk_index
        if 0 < risk_index <= 1.0:
            # Convert from 0-1 scale to 0-100 scale
            normalized_risk_index = risk_index * 100
        # If risk_index is 0, keep it as 0 (works for both scales)
        
        # Get risk level info using normalized value
        dri_info = self.calculator.calculate_dri(normalized_risk_index)
        
        # Color mapping
        color_map = {
            "green": "#4CAF50",
            "yellow": "#FFC107",
            "orange": "#FF9800",
            "red": "#F44336",
            "darkred": "#B71C1C"
        }
        color = color_map.get(dri_info["color"], "#9E9E9E")
        
        # Format disease name (capitalize, handle underscores)
        display_name = disease.replace('_', ' ').title()
        
        # Create professional card with HTML/CSS - Enhanced Visibility
        card_html = f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid {color};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h4 style="margin: 0; color: #0f172a; font-size: 1rem; font-weight: 600;">
                    {display_name}
                </h4>
                <span style="
                    background: {color};
                    color: #000000;
                    padding: 0.375rem 0.75rem;
                    border-radius: 16px;
                    font-size: 0.75rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">{dri_info['level']}</span>
            </div>
                <div style="margin-top: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: #64748b; font-size: 0.8125rem; font-weight: 500;">Risk Index</span>
                    <span style="color: #0f172a; font-size: 1.25rem; font-weight: 700;">{risk_index:.1f}</span>
                </div>
                <div style="
                    background: #f1f5f9;
                    border-radius: 6px;
                    height: 8px;
                    overflow: hidden;
                    margin-top: 0.5rem;
                    box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
                ">
                    <div style="
                        background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
                        height: 100%;
                        width: {min(100, normalized_risk_index)}%;
                        transition: width 0.3s ease;
                        border-radius: 6px;
                    "></div>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


# Convenience functions for direct use
def display_dri_card(disease: str, risk_index: float, show_description: bool = True) -> None:
    """Convenience function to display DRI card"""
    display = RiskDisplay()
    display.display_dri_card(disease, risk_index, show_description)


def display_composite_score(composite_data: Dict) -> None:
    """Convenience function to display composite score"""
    display = RiskDisplay()
    display.display_composite_score_card(composite_data)

