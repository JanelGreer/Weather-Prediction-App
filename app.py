import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import sqlite3
from weather_metrics import WeatherMetrics
from weather_sql import WeatherData, DatabaseHandler
from utils import get_coordinates_from_location, validate_date, format_weather_data

# Set page configuration
st.set_page_config(
    page_title="Weather Prediction System",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None

def main():
    st.title("⛅ Weather Prediction System")
    st.markdown("### 5-Year Historical Weather Analysis for Event Planning")
    
    # Sidebar for input controls
    with st.sidebar:
        st.header("📍 Location & Date Settings")
        
        # Location input method selection
        location_method = st.radio(
            "Choose location input method:",
            ["Search by City/Address", "Enter Coordinates Manually"]
        )
        
        latitude = None
        longitude = None
        
        if location_method == "Search by City/Address":
            location_input = st.text_input(
                "Enter city name or address:",
                placeholder="e.g., Miami, FL or New York City"
            )
            
            if location_input and st.button("🔍 Get Coordinates"):
                with st.spinner("Looking up coordinates..."):
                    coords = get_coordinates_from_location(location_input)
                    if coords:
                        latitude, longitude = coords
                        st.success(f"Found: {latitude:.4f}°N, {longitude:.4f}°W")
                        st.session_state.latitude = latitude
                        st.session_state.longitude = longitude
                    else:
                        st.error("Location not found. Please try a different search term.")
            
            # Use stored coordinates if available
            if 'latitude' in st.session_state and 'longitude' in st.session_state:
                latitude = st.session_state.latitude
                longitude = st.session_state.longitude
                
        else:
            latitude = st.number_input(
                "Latitude:",
                min_value=-90.0,
                max_value=90.0,
                value=25.7743,
                step=0.0001,
                format="%.4f"
            )
            longitude = st.number_input(
                "Longitude:",
                min_value=-180.0,
                max_value=180.0,
                value=-80.1937,
                step=0.0001,
                format="%.4f"
            )
        
        st.markdown("---")
        
        # Date input
        st.subheader("📅 Target Date")
        target_date = st.date_input(
            "Select your event date:",
            value=date(2025, 6, 23),
            min_value=date(1940, 1, 1),
            max_value=date(2030, 12, 31)
        )
        
        st.markdown("---")
        
        # Analysis button
        if st.button("Analyze Weather Data", type="primary", use_container_width=True):
            if latitude is not None and longitude is not None:
                if validate_date(target_date.month, target_date.day, target_date.year):
                    run_weather_analysis(latitude, longitude, target_date)
                else:
                    st.error("Invalid date selected. Please check your input.")
            else:
                st.error("Please provide valid coordinates.")
        
        # Database query section
        st.markdown("---")
        st.subheader("🔴 Previous Analyses")
        if st.button("View Stored Data", use_container_width=True):
            show_database_records()

    # Main content area
    if st.session_state.analysis_complete and st.session_state.weather_data is not None:
        display_analysis_results()
    else:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to the Weather Prediction System
            
            This application analyzes **5 years of historical weather data** to help you make informed decisions about outdoor events, weddings, or any weather-dependent activities.
            
            ### ➜ What it does:
            - Fetches historical weather data from OpenMeteo API
            - Analyzes temperature, wind speed, and precipitation patterns
            - Provides statistical insights (averages, minimums, maximums)
            - Stores results for future reference
            
            ### ➜ Get started:
            1. Enter your location (search by city or use coordinates)
            2. Select your target date
            3. Click "Analyze Weather Data"
            
            ### ➜ You'll receive:
            - Comprehensive weather statistics
            - Interactive visualizations
            - Historical data trends
            - Weather risk assessment
            """)

def run_weather_analysis(latitude, longitude, target_date):
    """Run the weather analysis for the given parameters"""
    try:
        with st.spinner("🌐 Fetching weather data... This may take a moment."):
            # Create WeatherMetrics instance
            metrics = WeatherMetrics(
                latitude=latitude,
                longitude=longitude,
                month=target_date.month,
                day=target_date.day,
                year=target_date.year
            )
            
            # Store in database
            weather_data = WeatherData(
                longitude=metrics.longitude,
                latitude=metrics.latitude,
                month=metrics.month,
                day=metrics.day,
                year=metrics.year,
                avg_temp=metrics.avg_temp,
                min_temp=metrics.min_temp,
                max_temp=metrics.max_temp,
                avg_wind=metrics.avg_wind,
                min_wind=metrics.min_wind,
                max_wind=metrics.max_wind,
                sum_precip=metrics.sum_precip,
                min_precip=metrics.min_precip,
                max_precip=metrics.max_precip
            )
            
            db_handler = DatabaseHandler()
            db_handler.insert_data(weather_data)
            
            # Store the data as a dictionary instead of SQLAlchemy object
            weather_dict = {
                'latitude': metrics.latitude,
                'longitude': metrics.longitude,
                'month': metrics.month,
                'day': metrics.day,
                'year': metrics.year,
                'avg_temp': metrics.avg_temp,
                'min_temp': metrics.min_temp,
                'max_temp': metrics.max_temp,
                'avg_wind': metrics.avg_wind,
                'min_wind': metrics.min_wind,
                'max_wind': metrics.max_wind,
                'sum_precip': metrics.sum_precip,
                'min_precip': metrics.min_precip,
                'max_precip': metrics.max_precip
            }
            
            # Store in session state
            st.session_state.metrics = metrics
            st.session_state.weather_data = weather_dict
            st.session_state.analysis_complete = True
            
            st.success("✅ Analysis complete!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.error("Please check your internet connection and try again.")

def display_analysis_results():
    """Display the weather analysis results with visualizations"""
    metrics = st.session_state.metrics
    weather_data = st.session_state.weather_data
    
    # Header with location info
    st.header(f"📊 Weather Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Latitude", f"{weather_data['latitude']:.4f}°")
    with col2:
        st.metric("📍 Longitude", f"{weather_data['longitude']:.4f}°")
    with col3:
        st.metric("📅 Target Date", f"{weather_data['month']}/{weather_data['day']}/{weather_data['year']}")
    
    st.markdown("---")
    
    # Key Metrics Overview
    st.subheader("🔴 Key Weather Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Avg Temperature",
            f"{weather_data['avg_temp']:.1f}°F",
            delta=f"Range: {weather_data['min_temp']:.1f}°F - {weather_data['max_temp']:.1f}°F"
        )
    
    with col2:
        st.metric(
            "💨 Avg Wind Speed",
            f"{weather_data['avg_wind']:.1f} mph",
            delta=f"Max: {weather_data['max_wind']:.1f} mph"
        )
    
    with col3:
        st.metric(
            "🌧️ Total Precipitation",
            f"{weather_data['sum_precip']:.2f} in",
            delta=f"Max daily: {weather_data['max_precip']:.2f} in"
        )
    
    with col4:
        # Weather risk assessment
        risk_score = calculate_weather_risk(weather_data)
        st.metric("⚠️ Weather Risk", risk_score["level"], delta=risk_score["description"])
    
    st.markdown("---")
    
    # Detailed visualizations
    create_weather_visualizations(metrics)
    
    # Detailed statistics table
    st.subheader("📈 Detailed Statistics")
    create_statistics_table(weather_data)
    
    # Export functionality
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Download Data as CSV"):
            # Create a simple WeatherData-like object for the format function
            class SimpleWeatherData:
                def __init__(self, data_dict):
                    for key, value in data_dict.items():
                        setattr(self, key, value)
            
            weather_obj = SimpleWeatherData(weather_data)
            csv_data = format_weather_data(weather_obj)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"weather_analysis_{weather_data['latitude']}_{weather_data['longitude']}_{weather_data['month']}-{weather_data['day']}-{weather_data['year']}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🔄 Start New Analysis"):
            st.session_state.analysis_complete = False
            st.session_state.weather_data = None
            st.session_state.metrics = None
            st.rerun()

def create_weather_visualizations(metrics):
    """Create interactive visualizations of the weather data"""
    
    # Get the raw data for visualizations
    raw_data = metrics.get_data_for_date()
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["🌡️ Temperature", "💨 Wind Speed", "🌧️ Precipitation"])
    
    with tab1:
        # Temperature visualization
        fig_temp = go.Figure()
        
        years = [date.year for date in raw_data['date']]
        
        fig_temp.add_trace(go.Scatter(
            x=years,
            y=raw_data['temperature_2m_max'],
            mode='lines+markers',
            name='Max Temperature',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=years,
            y=raw_data['temperature_2m_min'],
            mode='lines+markers',
            name='Min Temperature',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=years,
            y=raw_data['temperature_2m_mean'],
            mode='lines+markers',
            name='Mean Temperature',
            line=dict(color='orange', width=3),
            marker=dict(size=8)
        ))
        
        fig_temp.update_layout(
            title='5-Year Temperature Trends',
            xaxis_title='Year',
            yaxis_title='Temperature (°F)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with tab2:
        # Wind speed visualization
        fig_wind = go.Figure()
        
        fig_wind.add_trace(go.Scatter(
            x=years,
            y=raw_data['wind_speed_10m_max'],
            mode='lines+markers',
            name='Max Wind Speed',
            line=dict(color='green', width=3),
            marker=dict(size=8),
            fill='tonexty'
        ))
        
        fig_wind.add_trace(go.Scatter(
            x=years,
            y=raw_data['wind_gusts_10m_max'],
            mode='lines+markers',
            name='Max Wind Gusts',
            line=dict(color='darkgreen', width=3),
            marker=dict(size=8)
        ))
        
        fig_wind.update_layout(
            title='5-Year Wind Speed Trends',
            xaxis_title='Year',
            yaxis_title='Wind Speed (mph)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_wind, use_container_width=True)
    
    with tab3:
        # Precipitation visualization
        fig_precip = go.Figure()
        
        fig_precip.add_trace(go.Bar(
            x=years,
            y=raw_data['precipitation_sum'],
            name='Daily Precipitation',
            marker_color='lightblue',
            text=[f"{val:.2f} in" for val in raw_data['precipitation_sum']],
            textposition='auto'
        ))
        
        fig_precip.update_layout(
            title='5-Year Precipitation Patterns',
            xaxis_title='Year',
            yaxis_title='Precipitation (inches)',
            height=400
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)

def create_statistics_table(weather_data):
    """Create a detailed statistics table"""
    
    stats_data = {
        'Metric': [
            'Temperature (°F)',
            'Temperature (°F)',
            'Temperature (°F)',
            'Wind Speed (mph)',
            'Wind Speed (mph)',
            'Wind Speed (mph)',
            'Precipitation (inches)',
            'Precipitation (inches)',
            'Precipitation (inches)'
        ],
        'Statistic': [
            'Average', 'Minimum', 'Maximum',
            'Average', 'Minimum', 'Maximum',
            'Total', 'Minimum', 'Maximum'
        ],
        'Value': [
            f"{weather_data['avg_temp']:.2f}",
            f"{weather_data['min_temp']:.2f}",
            f"{weather_data['max_temp']:.2f}",
            f"{weather_data['avg_wind']:.2f}",
            f"{weather_data['min_wind']:.2f}",
            f"{weather_data['max_wind']:.2f}",
            f"{weather_data['sum_precip']:.2f}",
            f"{weather_data['min_precip']:.2f}",
            f"{weather_data['max_precip']:.2f}"
        ]
    }
    
    df = pd.DataFrame(stats_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def calculate_weather_risk(weather_data):
    """Calculate a simple weather risk assessment"""
    risk_factors = 0
    
    # High temperature risk
    if weather_data['max_temp'] > 90:
        risk_factors += 2
    elif weather_data['max_temp'] > 85:
        risk_factors += 1
    
    # High wind risk
    if weather_data['max_wind'] > 25:
        risk_factors += 2
    elif weather_data['max_wind'] > 15:
        risk_factors += 1
    
    # Precipitation risk
    if weather_data['sum_precip'] > 1.0:
        risk_factors += 2
    elif weather_data['sum_precip'] > 0.5:
        risk_factors += 1
    
    if risk_factors >= 4:
        return {"level": "High", "description": "Consider indoor alternatives"}
    elif risk_factors >= 2:
        return {"level": "Medium", "description": "Have backup plans ready"}
    else:
        return {"level": "Low", "description": "Good conditions expected"}

def show_database_records():
    """Display stored weather analysis records"""
    try:
        # Connect to database and fetch records
        import sqlite3
        conn = sqlite3.connect('weather.db')
        query = """
        SELECT latitude, longitude, month, day, year, avg_temp, max_wind, sum_precip
        FROM weather_data
        ORDER BY year DESC, month DESC, day DESC
        LIMIT 10
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            st.subheader("📚 Recent Analyses")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No previous analyses found in the database.")
            
    except Exception as e:
        st.error(f"Error loading database records: {str(e)}")

if __name__ == "__main__":
    main()
