import yr_weather as yw
import os 
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests

load_dotenv()

class WeatherAPI:
    def __init__(self):
        try:
            self.headers = {
                "User-Agent": f"{os.environ.get('USER_AGENT')}",
            }
            self.my_client = yw.Locationforecast(headers=self.headers)
        except Exception as e:
            print(f"Error initializing WeatherAPI: {e}")
        
    def get_forecast(self, latitude, longitude):
        try:
            forecast = self.my_client.get_forecast(latitude, longitude)
            return forecast
        except requests.exceptions.RequestException as e:
            print(f"Network error while fetching forecast: {e}")
        except Exception as e:
            print(f"Error fetching forecast: {e}")
    
    def get_air_temperature(self, latitude, longitude):
        try:
            air_temperature = self.my_client.get_air_temperature(latitude, longitude)
            return air_temperature
        except Exception as e:
            print(f"Error fetching air temperature: {e}")
            return None
    
    def get_tomorrow_forecast(self, latitude, longitude, days = 1):
        """Get the weather forecast for the same time tomorrow."""
        try:
            forecast = self.get_forecast(latitude, longitude)
            if forecast:
                # Accessing the private _timeseries attribute
                timeseries = forecast._timeseries

                # Get the current time and add 24 hours to get tomorrow's time
                now = datetime.now()
                tomorrow = now + timedelta(days=days)
                midday_tomorrow = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)  

                for time_step in timeseries:
                    forecast_time = datetime.strptime(time_step['time'], "%Y-%m-%dT%H:%M:%SZ")

                    
                    # Compare both the date and time to match exactly midday tomorrow
                    if forecast_time == midday_tomorrow:
                        return time_step


                print("Could not find a forecast for tomorrow.")
            return None
        except Exception as e:
            print(f"Error fetching tomorrow's forecast: {e}")
            return None
    
    def get_precipitation(self, latitude, longitude):
        try:
            forecast = self.get_forecast(latitude, longitude)
            if forecast:
                forecast_now = forecast.now()
                next_6_hrs = forecast_now.next_6_hours
                precipitation = next_6_hrs.details.precipitation_amount
                return precipitation
            else:
                return None
        except Exception as e:
            print(f"Error fetching precipitation data: {e}")
            return None

    def get_wind_data(self, latitude, longitude):
        try:
            forecast = self.get_forecast(latitude, longitude)
            if forecast:
                forecast_now = forecast.now()
                wind_speed = forecast_now.details.wind_speed
                return wind_speed
            else:
                return None
        except Exception as e:
            print(f"Error fetching wind data: {e}")
            return None

    def get_uv_index(self, latitude, longitude):
        try:
            forecast = self.get_forecast(latitude, longitude)
            if forecast:
                forecast_now = forecast.now()
                uv_index = forecast_now.details.ultraviolet_index_clear_sky
                return uv_index
            else:
                return None
        except Exception as e:
            print(f"Error fetching UV index: {e}")
            return None

    def calculate_wind_chill(self, temperature, wind_speed):
        """Calculate wind chill temperature if the temperature is below 10°C."""
        if temperature < 10 and wind_speed > 0:
            wind_chill = 13.12 + 0.6215 * temperature - 11.37 * (wind_speed**0.16) + 0.3965 * temperature * (wind_speed**0.16)
            return round(wind_chill, 2)
        return temperature

    def suggest_clothing(self, latitude, longitude, activity="general", time_of_day="day"):
        try:
            temperature = self.get_air_temperature(latitude, longitude)
            precipitation = self.get_precipitation(latitude, longitude)
            wind_speed = self.get_wind_data(latitude, longitude)
            uv_index = self.get_uv_index(latitude, longitude)

            suggestions = []

            if temperature and wind_speed:
                # Apply wind chill to temperature if applicable
                adjusted_temp = self.calculate_wind_chill(temperature, wind_speed)

                # Include actual and "feels-like" temperature in the suggestion
                suggestions.append(f"The actual temperature is {temperature}°C.")
                if adjusted_temp != temperature:
                    suggestions.append(f"Due to wind, it feels like {adjusted_temp}°C.")

                # More nuanced temperature-based clothing suggestions
                if adjusted_temp < 0:
                    suggestions.append("Wear a heavy winter coat, thermal layers, gloves, scarf, hat, and warm boots.")
                elif 0 <= adjusted_temp < 5:
                    suggestions.append("Wear a thick jacket, scarf, gloves, and warm layers.")
                elif 5 <= adjusted_temp < 10:
                    suggestions.append("A jacket with a sweater or hoodie, and consider gloves.")
                elif 10 <= adjusted_temp < 15:
                    suggestions.append("Wear a light jacket or sweater, with long sleeves and pants.")
                elif 15 <= adjusted_temp < 20:
                    suggestions.append("A light sweater or jacket should be fine, maybe a T-shirt underneath.")
                elif 20 <= adjusted_temp < 25:
                    suggestions.append("Comfortable clothing like a T-shirt and jeans. A light sweater for evenings.")
                else:
                    suggestions.append("Light clothing like shorts and a T-shirt. Consider sunscreen if it's sunny.")

            # Add precipitation-based suggestions
            if precipitation and precipitation > 0:
                suggestions.append(f"Precipitation expected: {precipitation} mm. Bring an umbrella or wear a waterproof jacket.")
                if precipitation > 5:
                    suggestions.append("Wear waterproof shoes or boots.")

            # Wind-based suggestions
            if wind_speed and wind_speed > 5:
                suggestions.append(f"Wind speed: {wind_speed} m/s. Wear a windproof jacket, especially if you're cycling or walking outside.")
                if activity == "biking":
                    suggestions.append("Consider extra wind protection for biking, like a windbreaker.")

            # UV-based suggestions
            if uv_index and uv_index > 3:
                suggestions.append(f"UV index: {uv_index}. Wear sunglasses, and apply sunscreen, especially during midday.")

            # Time of day adjustment
            if time_of_day == "night":
                suggestions.append("Evening temperatures are cooler. Carry an extra layer.")

            # Final suggestion summary
            if suggestions:
                return "Clothing Suggestions: " + " ".join(suggestions)
            else:
                return "No significant weather changes. Dress comfortably."

        except Exception as e:
            print(f"Error providing clothing suggestions: {e}")
            return "Unable to provide clothing suggestions at the moment."
    
    def suggest_clothing_for_tomorrow(self, latitude, longitude, activity="general", time_of_day="day"):
        try:
            forecast = self.get_tomorrow_forecast(latitude, longitude)
            if forecast:
                # Extract necessary data from the forecast
                air_temperature = forecast['data']['instant']['details']['air_temperature']
                wind_speed = forecast['data']['instant']['details']['wind_speed']
                precipitation = forecast['data']['next_6_hours']['details']['precipitation_amount']
                uv_index = forecast['data']['instant']['details'].get('ultraviolet_index_clear_sky', None)

                suggestions = []
                # Include the actual temperature in the suggestion
                suggestions.append(f"Tomorrow's temperature will be {air_temperature}°C.")

                # More nuanced temperature-based clothing suggestions
                if air_temperature < 0:
                    suggestions.append("Wear a heavy winter coat, thermal layers, gloves, scarf, hat, and warm boots.")
                elif 0 <= air_temperature < 5:
                    suggestions.append("Wear a thick jacket, scarf, gloves, and warm layers.")
                elif 5 <= air_temperature < 10:
                    suggestions.append("A jacket with a sweater or hoodie, and consider gloves.")
                elif 10 <= air_temperature < 15:
                    suggestions.append("Wear a light jacket or sweater, with long sleeves and pants.")
                elif 15 <= air_temperature < 20:
                    suggestions.append("A light sweater or jacket should be fine, maybe a T-shirt underneath.")
                elif 20 <= air_temperature < 25:
                    suggestions.append("Comfortable clothing like a T-shirt and jeans. A light sweater for evenings.")
                else:
                    suggestions.append("Light clothing like shorts and a T-shirt. Consider sunscreen if it's sunny.")

                # Add precipitation-based suggestions
                if precipitation and precipitation > 0:
                    suggestions.append(f"Precipitation expected: {precipitation} mm. Bring an umbrella or wear a waterproof jacket.")
                    if precipitation > 5:
                        suggestions.append("Wear waterproof shoes or boots.")

                # Wind-based suggestions
                if wind_speed and wind_speed > 5:
                    suggestions.append(f"Wind speed: {wind_speed} m/s. Wear a windproof jacket, especially if you're cycling or walking outside.")
                    if activity == "biking":
                        suggestions.append("Consider extra wind protection for biking, like a windbreaker.")

                # UV-based suggestions
                if uv_index and uv_index > 3:
                    suggestions.append(f"UV index: {uv_index}. Wear sunglasses, and apply sunscreen, especially during midday.")

                # Final suggestion summary
                if suggestions:
                    return "Clothing Suggestions for Tomorrow: " + " ".join(suggestions)
                else:
                    return "No significant weather changes for tomorrow. Dress comfortably."

            return "Unable to retrieve tomorrow's forecast."
        except Exception as e:
            print(f"Error providing clothing suggestions for tomorrow: {e}")
            return "Unable to provide clothing suggestions for tomorrow at the moment."


if __name__ == "__main__":
    api = WeatherAPI()
    try:
        latitude = os.environ.get('LATITUDE')
        longitude = os.environ.get('LONGITUDE')
        activity = os.environ.get('ACTIVITY', 'general')  # Optional: Can specify 'biking', 'walking', etc.
        time_of_day = os.environ.get('TIME_OF_DAY', 'day')  # Optional: 'day' or 'night'
        
        if latitude and longitude:
            # Get today's clothing suggestion
            print("Today's Suggestion:")
            print(api.suggest_clothing(latitude, longitude, activity=activity, time_of_day=time_of_day))

            # Get tomorrow's clothing suggestion
            print("\nTomorrow's Suggestion:")
            print(api.suggest_clothing_for_tomorrow(latitude, longitude, activity=activity, time_of_day=time_of_day))

        else:
            print("Latitude and longitude are not set in the environment variables.")
    except Exception as e:
        print(f"Error during execution: {e}")
