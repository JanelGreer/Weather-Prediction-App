import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import pandas as pd
import calendar

def get_coordinates_from_location(location_name):
    """
    Convert location name to latitude and longitude coordinates
    Returns tuple (latitude, longitude) or None if not found
    """
    try:
        # Initialize geocoder with a user agent
        geolocator = Nominatim(user_agent="weather_prediction_app")
        
        # Get location
        location = geolocator.geocode(location_name, timeout=10)
        
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.error(f"Geocoding service error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return None

def validate_date(month, day, year):
    """
    Validate if the given date is valid
    Returns True if valid, False otherwise
    """
    try:
        # Check basic ranges
        if not (1 <= month <= 12):
            return False
        
        if not (1940 <= year <= 2030):
            return False
        
        # Check if day is valid for the given month
        if month in [1, 3, 5, 7, 8, 10, 12]:  # 31-day months
            if not (1 <= day <= 31):
                return False
        elif month in [4, 6, 9, 11]:  # 30-day months
            if not (1 <= day <= 30):
                return False
        else:  # February
            # Check for leap year
            if calendar.isleap(year):
                if not (1 <= day <= 29):
                    return False
            else:
                if not (1 <= day <= 28):
                    return False
        
        return True
        
    except Exception:
        return False

def format_weather_data(weather_data):
    """
    Format weather data for CSV export
    Returns CSV string
    """
    try:
        data_dict = {
            'Latitude': [weather_data.latitude],
            'Longitude': [weather_data.longitude],
            'Month': [weather_data.month],
            'Day': [weather_data.day],
            'Year': [weather_data.year],
            'Average_Temperature_F': [weather_data.avg_temp],
            'Minimum_Temperature_F': [weather_data.min_temp],
            'Maximum_Temperature_F': [weather_data.max_temp],
            'Average_Wind_Speed_mph': [weather_data.avg_wind],
            'Minimum_Wind_Speed_mph': [weather_data.min_wind],
            'Maximum_Wind_Speed_mph': [weather_data.max_wind],
            'Total_Precipitation_inches': [weather_data.sum_precip],
            'Minimum_Precipitation_inches': [weather_data.min_precip],
            'Maximum_Precipitation_inches': [weather_data.max_precip]
        }
        
        df = pd.DataFrame(data_dict)
        return df.to_csv(index=False)
        
    except Exception as e:
        st.error(f"Error formatting data for export: {str(e)}")
        return ""

def get_location_display_name(latitude, longitude):
    """
    Get a human-readable location name from coordinates
    Returns location name string or coordinates if name not found
    """
    try:
        geolocator = Nominatim(user_agent="weather_prediction_app")
        location = geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
        
        if location:
            return location.address
        else:
            return f"{latitude:.4f}°N, {longitude:.4f}°W"
            
    except Exception:
        return f"{latitude:.4f}°N, {longitude:.4f}°W"

def calculate_weather_suitability_score(weather_data):
    """
    Calculate a weather suitability score for outdoor events
    Returns score from 0-100 (higher is better)
    """
    score = 100
    
    # Temperature scoring (ideal range: 70-80°F)
    if weather_data.avg_temp < 60 or weather_data.avg_temp > 90:
        score -= 30
    elif weather_data.avg_temp < 70 or weather_data.avg_temp > 80:
        score -= 15
    
    # Wind speed scoring (ideal: < 10 mph)
    if weather_data.max_wind > 25:
        score -= 25
    elif weather_data.max_wind > 15:
        score -= 15
    elif weather_data.max_wind > 10:
        score -= 10
    
    # Precipitation scoring (ideal: minimal precipitation)
    if weather_data.sum_precip > 1.0:
        score -= 20
    elif weather_data.sum_precip > 0.5:
        score -= 10
    elif weather_data.sum_precip > 0.1:
        score -= 5
    
    return max(0, score)

def get_weather_recommendations(weather_data):
    """
    Generate weather-based recommendations for event planning
    Returns list of recommendation strings
    """
    recommendations = []
    
    # Temperature recommendations
    if weather_data.avg_temp > 85:
        recommendations.append("🌡️ High temperatures expected - consider providing shade and hydration stations")
    elif weather_data.avg_temp < 65:
        recommendations.append("🧥 Cool temperatures expected - inform guests to bring warm clothing")
    
    # Wind recommendations
    if weather_data.max_wind > 20:
        recommendations.append("💨 High wind speeds possible - secure decorations and avoid tall structures")
    elif weather_data.max_wind > 10:
        recommendations.append("🎪 Moderate winds expected - ensure tents and displays are properly anchored")
    
    # Precipitation recommendations
    if weather_data.sum_precip > 0.5:
        recommendations.append("☔ Significant precipitation likely - have indoor backup plans ready")
    elif weather_data.sum_precip > 0.1:
        recommendations.append("🌧️ Some precipitation possible - consider covered areas or umbrellas")
    
    # General recommendations
    if weather_data.max_temp - weather_data.min_temp > 20:
        recommendations.append("🌡️ Large temperature variation expected - advise guests on layered clothing")
    
    if not recommendations:
        recommendations.append("✅ Weather conditions appear favorable for outdoor activities")
    
    return recommendations
