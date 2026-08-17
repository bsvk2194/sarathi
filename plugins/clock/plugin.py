"""
Clock Plugin for SARATHI.
"""

from datetime import datetime

from core.plugins.base import Plugin


class ClockPlugin(Plugin):

    id = "clock"

    name = "Clock"

    version = "1.0.0"

    description = "Provides date and time."

    def execute(self, request):

        now = datetime.now()

        action = request.action

        if action == "get_time":

            return self.get_time(now)

        elif action == "get_date":

            return self.get_date(now)

        elif action == "get_datetime":

            return self.get_datetime(now)

        elif action == "get_timezone":

            return self.get_timezone(now)

        else:

            raise ValueError(
                f"Unknown action '{action}'."
            )

    def get_time(self, now):

        return now.strftime("%H:%M:%S")

    def get_date(self, now):

        return now.strftime("%Y-%m-%d")

    def get_datetime(self, now):

        return now.strftime("%Y-%m-%d %H:%M:%S")

    def get_timezone(self, now):

        return str(now.astimezone().tzinfo)