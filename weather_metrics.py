# C.2: Imports Needed for C.2 Methods

import openmeteo_requests
import requests_cache
import pandas as pd
pd.set_option('display.max_columns', 10) #Expand Columns
from retry_requests import retry
from datetime import datetime

# C.1: Add Instance Variables for Location & Date

class WeatherMetrics:
    def __init__(self, latitude, longitude, month, day, year):
        self.latitude = latitude
        self.longitude = longitude
        self.month = month
        self.day = day
        self.year = year
        # Add Averages/Minimums/Maximums of Variables
        self.avg_temp = 0
        self.min_temp = 0
        self.max_temp = 0
        self.avg_wind = 0
        self.min_wind = 0
        self.max_wind = 0
        self.sum_precip = 0
        self.min_precip = 0
        self.max_precip = 0

        # Fill Out Variables with Chosen Date
        self.fill_out_class()

    def fill_out_class(self):
        # Grabbing Data from Website API
        chosen_date_data = self.get_data_for_date()

        # Calls Methods for Getting Averages/Max/Sum and Calculates Data
        self.avg_temp = self.calc_avg_temp(chosen_date_data)
        self.min_temp = chosen_date_data['temperature_2m_min'].min()
        self.max_temp = chosen_date_data['temperature_2m_max'].max()
        self.avg_wind = chosen_date_data['wind_speed_10m_max'].mean()
        self.min_wind = chosen_date_data['wind_speed_10m_max'].min()
        self.max_wind = self.calc_wind_speed_max(chosen_date_data)
        self.sum_precip = self.calc_total_precip(chosen_date_data)
        self.min_precip = chosen_date_data['precipitation_sum'].min()
        self.max_precip = chosen_date_data['precipitation_sum'].max()

    # Create Method to Call Weather API
    def get_data_for_date(self):

# C.1 Summary: Created Class with Variables, Filled Out Variables with Methods

# C.2: Create Loop to Go Back 5 Years

        # Create Structure for Adding Each Year's Data
        chosen_date_data = {
        'date': [],
        'temperature_2m_max': [],
        'temperature_2m_min': [],
        'temperature_2m_mean': [],
        'precipitation_sum': [],
        'wind_speed_10m_max': [],
        'wind_gusts_10m_max': [],
        }
        # Looping Back 5 Years
        for i in range(1, 6):
            start_date = datetime(datetime.now().year - i, self.month, self.day)
            end_date = start_date #Grabbing only 1 date, so start date = end date
            data_for_that_year = self.call_api(start_date, end_date)
            chosen_date_data['date'].append(data_for_that_year['date'][0]) #Append Data
            # Adding Each Years Worth of Data to Our Object
            chosen_date_data['temperature_2m_max'].append(data_for_that_year['temperature_2m_max'][0])
            chosen_date_data['temperature_2m_min'].append(data_for_that_year['temperature_2m_min'][0])
            chosen_date_data['temperature_2m_mean'].append(data_for_that_year['temperature_2m_mean'][0])
            chosen_date_data['precipitation_sum'].append(data_for_that_year['precipitation_sum'][0])
            chosen_date_data['wind_speed_10m_max'].append(data_for_that_year['wind_speed_10m_max'][0])
            chosen_date_data['wind_gusts_10m_max'].append(data_for_that_year['wind_gusts_10m_max'][0])

        # Panda Library
        all = pd.DataFrame(data=chosen_date_data)

        return all

    # Calling API with Specific Start and End Date
    def call_api(self, start_date, end_date):

        # C.2: Generated Weather API - START

        # Set up the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://archive-api.open-meteo.com/v1/archive"

        # Continue Website Weather API - Sets Query Parameters for API GET Request
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "precipitation_sum",
                      "wind_speed_10m_max", "wind_gusts_10m_max"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(5).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        # Copied Over for Key Names
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

        return daily_data

# C.2: Generated Weather API - END

    # C.2: Write Out Methods

    # Calculate the Average Temperature
    @staticmethod
    def calc_avg_temp(data):
        return data['temperature_2m_mean'].mean()

    # Calculate Maximum Wind Speed
    @staticmethod
    def calc_wind_speed_max(data):
        return data['wind_speed_10m_max'].max()

    # Calculate the Total Precipitation
    @staticmethod
    def calc_total_precip(data):
        return data['precipitation_sum'].sum()

# C.2 Summary: Called API, Created Loop, Performed Calculations
