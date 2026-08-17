"""
Plugin Analytics for SARATHI.
"""

from datetime import datetime


class PluginAnalytics:

    def __init__(self):

        self.requests = []

    def log_request(
        self,
        plugin,
        action,
        success,
        latency
    ):

        self.requests.append(
            {
                "timestamp": datetime.now(),
                "plugin": plugin,
                "action": action,
                "success": success,
                "latency": latency
            }
        )

    def get_requests(self):

        return self.requests

    def average_latency(
        self,
        plugin
    ):

        values = [
            r["latency"]
            for r in self.requests
            if r["plugin"] == plugin
        ]

        if not values:

            return None

        return sum(values) / len(values)


analytics = PluginAnalytics()