"""
Weather Plugin for SARATHI.
"""

from core.plugins.base import Plugin

from plugins.weather.weather_api import weather_api


class WeatherPlugin(Plugin):

    id = "weather"

    name = "Weather"

    version = "1.0.0"

    description = "Provides weather information."

    def execute(self, request):

        data = weather_api.get_weather()

        current = data["current"]

        action = request.action

        if action == "get_weather":

            return {
                "temperature": current["temperature_2m"],
                "humidity": current["relative_humidity_2m"]
            }

        elif action == "get_temperature":

            return current["temperature_2m"]

        elif action == "get_humidity":

            return current["relative_humidity_2m"]

        else:

            raise ValueError(
                f"Unknown action '{action}'."
            )