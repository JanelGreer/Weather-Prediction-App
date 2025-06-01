
#C.4: Import SQLAlchemy ORM Module
from sqlalchemy import Column, Integer, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the Base Class for Models & Create Engine
engine = create_engine('sqlite:///weather.db')
base = declarative_base()


# C.4: Create Class for SQLite Table
class WeatherData(base):
    __tablename__ = "weather_data"  # Name of the SQLite table
    # Add Key & Increment
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Add Table Columns
    latitude = Column(Float)
    longitude = Column(Float)
    month = Column(Integer)
    day = Column(Integer)
    year = Column(Integer)
    avg_temp = Column(Float)
    min_temp = Column(Float)
    max_temp = Column(Float)
    avg_wind = Column(Float)
    min_wind = Column(Float)
    max_wind = Column(Float)
    sum_precip = Column(Float)
    min_precip = Column(Float)
    max_precip = Column(Float)

# Create Database Table
base.metadata.create_all(engine)

#C.4 Summary: Created SQL Table

#C.5: Create Class to Interact with Table
class DatabaseHandler:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
    # Insert Data into Table
    def insert_data(self, data):
        # Create New Session
        session = self.Session()
        try:
            session.add(data)
            # Commit Transaction
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            # Close Session
            session.close()

#C.5 Summary: Populate Table with Weather Data

#C.6: Query Data and Printing Formatted Data
    def fetch(self, month, day, year):
        # Create a New Session
        session = self.Session()
        try:
            #C.6: Query Chosen Date and Selecting First Record
            weather = session.query(WeatherData).filter(
                WeatherData.month == month, 
                WeatherData.day == day, 
                WeatherData.year == year
            ).first()
            
            if weather:
                #Print and Format Table Data
                print(f"Location Latitude: {weather.latitude:.2f}°")
                print(f"Location Longitude: {weather.longitude:.2f}°")
                print(f"Event Date: {weather.month}-{weather.day}-{weather.year}")
                print(f"5-Year Average Temperature: {weather.avg_temp:.2f}°F")
                print(f"5-Year Minimum Temperature: {weather.min_temp:.2f}°F")
                print(f"5-Year Maximum Temperature: {weather.max_temp:.2f}°F")
                print(f"5-Year Average Wind Speed: {weather.avg_wind:.2f} mph")
                print(f"5-Year Minimum Wind Speed: {weather.min_wind:.2f} mph")
                print(f"5-Year Maximum Wind Speed: {weather.max_wind:.2f} mph")
                print(f"5-Year Sum Precipitation: {weather.sum_precip:.2f} inches")
                print(f"5-Year Minimum Precipitation: {weather.min_precip:.2f} inches")
                print(f"5-Year Maximum Precipitation: {weather.max_precip:.2f} inches")
                return weather
            else:
                print("No data found for the specified date.")
                return None
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None
        finally:
            # Close the Session
            session.close()

    def get_all_records(self):
        """Fetch all weather records from the database"""
        session = self.Session()
        try:
            records = session.query(WeatherData).all()
            return records
        except Exception as e:
            print(f"Error fetching all records: {str(e)}")
            return []
        finally:
            session.close()

#C.6 Summary: Queried Table and Formatted Output
