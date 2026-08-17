"""
Weather API Client.
"""

import requests


class WeatherAPI:

    def get_weather(self):

        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=17.3850"
            "&longitude=78.4867"
            "&current=temperature_2m,relative_humidity_2m"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()


weather_api = WeatherAPI()