import requests
import pandas as pd
from datetime import datetime

print("API Demo Starting")
print("=" * 40)

# --------------------------------------------------------
# API #1: WEATHER DATA (Open-Meteo)
# Free, no API key needed, works for any location on Earth
# --------------------------------------------------------

def get_current_weather(lat, lon, city_name="Unknown"):
    """
    Get real-time weather for any location.
    No API key needed.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        current = data['current_weather']
        
        weather_info = {
            'city': city_name,
            'temperature_c': current['temperature'],
            'wind_speed_kmh': current['windspeed'],
            'time': current['time']
        }
        
        print(city_name + ":", weather_info['temperature_c'], "degrees C")
        print("  Wind:", weather_info['wind_speed_kmh'], "km/h")
        print("  Time:", weather_info['time'])
        return weather_info
    else:
        print("Failed to get weather for", city_name)
        print("Status code:", response.status_code)
        return None


print("TESTING WEATHER API")
print("-" * 40)

lagos = get_current_weather(6.5244, 3.3792, "Lagos")
print()
nairobi = get_current_weather(-1.2921, 36.8219, "Nairobi")
print()
london = get_current_weather(51.5074, -0.1278, "London")

# --------------------------------------------------------
# API #2: CURRENCY EXCHANGE RATES
# Free, no key required, updates daily
# --------------------------------------------------------

def get_exchange_rates(base_currency="USD"):
    """
    Get live exchange rates for all major currencies.
    """
    url = "https://open.er-api.com/v6/latest/" + base_currency
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        
        print("Exchange Rates (1", base_currency, "equals):")
        print("  Last Updated:", data['time_last_update_utc'])
        print()
        
        key_currencies = ['EUR', 'GBP', 'NGN', 'KES', 'ZAR', 'INR', 'CNY', 'JPY']
        for currency in key_currencies:
            if currency in rates:
                print("  " + currency + ":", rates[currency])
        
        return rates
    else:
        print("Failed to get exchange rates")
        return None


print()
print("TESTING EXCHANGE RATE API")
print("-" * 40)

rates = get_exchange_rates('USD')


def convert_currency(amount, from_currency, to_currency='USD'):
    """Convert any amount using live exchange rates."""
    all_rates = get_exchange_rates(to_currency)
    if all_rates and from_currency in all_rates:
        rate = all_rates[from_currency]
        converted = amount / rate
        print(str(amount) + " " + from_currency + " = " + str(round(converted, 2)) + " " + to_currency)
        return converted
    return None

print()
print("CURRENCY CONVERSION EXAMPLE")
print("-" * 40)

# A Nigerian client paid 500,000 NGN. What is that in USD?
convert_currency(500000, 'NGN', 'USD')


# --------------------------------------------------------
# API #3: RANDOM USER DATA (For Testing)
# Generate realistic test data for your automations
# --------------------------------------------------------

def generate_fake_users(count=10):
    """Generate realistic test data."""
    url = "https://randomuser.me/api/?results=" + str(count)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        users = []
        
        for user in data['results']:
            users.append({
                'first_name': user['name']['first'],
                'last_name': user['name']['last'],
                'email': user['email'],
                'phone': user['phone'],
                'city': user['location']['city'],
                'country': user['location']['country'],
                'age': user['dob']['age']
            })
        
        df = pd.DataFrame(users)
        print("Generated", len(df), "test users")
        return df
    return None


print()
print("TESTING RANDOM USER API")
print("-" * 40)

test_users = generate_fake_users(15)
print()
print("Sample users:")
print(test_users[['first_name', 'last_name', 'email', 'city']].head(8))

# --------------------------------------------------------
# API #4: THE MORNING DATA BRIEFING
# Aggregates data from multiple APIs into one report
# --------------------------------------------------------

def morning_data_briefing():
    """
    The script that runs every morning.
    Pulls from multiple APIs and creates a summary.
    """
    print("=" * 50)
    print("MORNING DATA BRIEFING")
    print(datetime.now().strftime('%B %d, %Y'))
    print("=" * 50)
    
    briefing = {}
    
    # Part 1: Weather for key locations
    print()
    print("WEATHER REPORT")
    print("-" * 40)
    locations = [
        ('Lagos', 6.5244, 3.3792),
        ('Nairobi', -1.2921, 36.8219),
        ('London', 51.5074, -0.1278)
    ]
    briefing['weather'] = []
    for city, lat, lon in locations:
        weather = get_current_weather(lat, lon, city)
        if weather:
            briefing['weather'].append(weather)
    
    # Part 2: Exchange rates
    print()
    print("EXCHANGE RATES")
    print("-" * 40)
    briefing['exchange_rates'] = get_exchange_rates('USD')
    
    # Part 3: Timestamp
    briefing['timestamp'] = datetime.now().isoformat()
    
    print()
    print("Briefing complete.")
    print("You could now:")
    print("  - Save to a database")
    print("  - Send as an email")
    print("  - Update a dashboard")
    print("  - Feed into a report")
    
    return briefing

print()
print("RUNNING COMPLETE MORNING BRIEFING")
print("=" * 50)

briefing = morning_data_briefing()

print()
print("BRIEFING DATA COLLECTED")
print("Weather reports:", len(briefing.get('weather', [])))
print("Exchange rates loaded:", briefing.get('exchange_rates') is not None)
print("Timestamp:", briefing.get('timestamp'))
# github.com/public-apis