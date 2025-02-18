import requests
import sqlite3
from datetime import datetime

#  Weather API
API_KEY = "f6abad6a4885cdf3b059d16d5f58a60d"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Database Setup
DB_FILE = "weather_history.db"

def initialize_database():
    """Initialize the SQLite database to store weather history."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WeatherHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            temperature TEXT,
            humidity TEXT,
            wind_speed TEXT,
            date_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(location, weather_info):
    """Save weather data to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO WeatherHistory (location, temperature, humidity, wind_speed, date_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        location,
        weather_info["Temperature"],
        weather_info["Humidity"],
        weather_info["Wind Speed"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def fetch_weather(location):
    """Fetch weather data from the OpenWeatherMap API."""
    global response
    try:
        # Construct request parameters
        params = {
            "q": location,  # Use 'q' for city name
            "appid": API_KEY,
            "units": "metric"  # Metric system for temperature in Celsius
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  
        data = response.json()

        weather_info = {
            "City": data["name"],
            "Temperature": f"{data['main']['temp']} °C",
            "Humidity": f"{data['main']['humidity']}%",
            "Wind Speed": f"{data['wind']['speed']} m/s",
        }
        return weather_info
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return {"Error": "Unauthorized: Check your API key."}
        elif response.status_code == 404:
            return {"Error": "City not found. Please check the location name."}
        else:
            return {"Error": f"HTTP error occurred: {http_err}"}
    except requests.exceptions.RequestException as e:
        return {"Error": f"Network error: {e}"}

def display_weather(weather_info):
    """Display weather data in a user-friendly format."""
    if "Error" in weather_info:
        print(weather_info["Error"])
    else:
        print("\nWeather Information:")
        for key, value in weather_info.items():
            print(f"{key}: {value}")

def console_interface():
    """Console-based user interface for the weather application."""
    print("Welcome to the Weather Application!")
    initialize_database()

    while True:
        location = input("\nEnter a city name (or type 'exit' to quit): ").strip()
        if location.lower() == "exit":
            print("Goodbye!")
            break

        weather_info = fetch_weather(location)
        display_weather(weather_info)

        if "Error" not in weather_info:
            save_to_database(location, weather_info)
            print("\nWeather data saved to history.")

def show_history():
    """Display weather history from the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT location, temperature, humidity, wind_speed, date_time FROM WeatherHistory")
    rows = cursor.fetchall()
    conn.close()

    print("\nWeather History:")
    for row in rows:
        print(f"{row[4]} - Location: {row[0]}, Temperature: {row[1]}, Humidity: {row[2]}, Wind Speed: {row[3]}")

def main():
    """Main function to run the weather application."""
    while True:
        print("\nOptions:")
        print("1. Fetch weather data")
        print("2. Show weather history")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()
        if choice == "1":
            console_interface()
        elif choice == "2":
            show_history()
        elif choice == "3":
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
