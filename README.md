# Weather Prediction System

A Streamlit web application that analyzes 5-year historical weather data for event planning and decision making.

## Features

- **Location Search**: Enter city names or coordinates directly
- **Historical Analysis**: Analyzes 5 years of weather data for any given date
- **Interactive Visualizations**: Temperature, wind speed, and precipitation charts
- **Weather Risk Assessment**: Automated risk scoring for outdoor events
- **Data Export**: Download analysis results as CSV
- **Database Storage**: Saves previous analyses for future reference

## Demo

This application transforms command-line weather analysis code into an interactive web interface, making weather prediction accessible to non-technical users.

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Data Source

Weather data is sourced from the OpenMeteo Historical Weather API, providing accurate historical weather information for locations worldwide.

## Technologies Used

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualizations
- **SQLAlchemy**: Database management
- **Geopy**: Location geocoding
- **Pandas**: Data manipulation
- **OpenMeteo API**: Historical weather data

## Project Structure

- `app.py`: Main Streamlit application
- `weather_metrics.py`: Core weather analysis logic
- `weather_sql.py`: Database models and handlers
- `utils.py`: Utility functions for data processing

## Usage

1. Select location input method (city search or coordinates)
2. Choose your target date
3. Click "Analyze Weather Data"
4. View comprehensive weather analysis with visualizations
5. Export results or start a new analysis

## Author

Janel Greer - [Portfolio](https://janelgreer.myportfolio.com/projects)