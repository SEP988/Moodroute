"""Weather service using OpenWeatherMap API."""
import requests
from config import Config


class WeatherService:
    BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

    def get_weather(self, latitude: float, longitude: float) -> dict:
        """Get current weather for a location."""
        api_key = Config.OPENWEATHER_API_KEY

        if not api_key or api_key == 'your_openweather_key_here':
            return self._fallback_weather()

        try:
            request_params = {
                'lat': latitude,
                'lon': longitude,
                'appid': api_key,
                'units': 'metric'
            }
            response = requests.get(self.BASE_URL, params=request_params, timeout=10)
            response.raise_for_status()
            weather_data = response.json()

            condition = weather_data['weather'][0]['main']
            temperature = weather_data['main']['temp']
            wind_speed_kmh = weather_data['wind']['speed'] * 3.6
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description'].capitalize()
            icon_code = weather_data['weather'][0]['icon']

            walkability = self._assess_walkability(condition, temperature, wind_speed_kmh)

            return {
                'condition': condition,
                'temp': round(temperature, 1),
                'wind': round(wind_speed_kmh, 1),
                'humidity': humidity,
                'description': description,
                'icon': self._get_emoji(condition),
                'icon_code': icon_code,
                'walkable': walkability
            }
        except Exception as api_error:
            print(f'[Weather] API error: {api_error}')
            return self._fallback_weather()

    def _assess_walkability(self, condition: str, temperature: float, wind_speed: float) -> str:
        """Assess if weather is safe for walking."""
        if condition in ['Thunderstorm', 'Tornado']:
            return 'dangerous'
        if condition in ['Snow', 'Squall'] or temperature < -5 or temperature > 42 or wind_speed > 60:
            return 'dangerous'
        if condition in ['Rain', 'Drizzle'] or temperature > 35 or wind_speed > 40:
            return 'poor'
        if condition in ['Mist', 'Fog', 'Haze'] or temperature > 32:
            return 'moderate'
        return 'good'

    def _get_emoji(self, condition: str) -> str:
        condition_emojis = {
            'Clear': '☀️', 'Clouds': '⛅', 'Rain': '🌧️',
            'Drizzle': '🌦️', 'Thunderstorm': '⛈️', 'Snow': '🌨️',
            'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '🌫️',
            'Smoke': '💨', 'Dust': '💨', 'Tornado': '🌪️'
        }
        return condition_emojis.get(condition, '🌤️')

    def _fallback_weather(self) -> dict:
        """Return reasonable default weather when API is unavailable."""
        return {
            'condition': 'Clear',
            'temp': 20.0,
            'wind': 12.0,
            'humidity': 55,
            'description': 'Weather data unavailable — assuming clear conditions',
            'icon': '🌤️',
            'icon_code': '02d',
            'walkable': 'good'
        }
