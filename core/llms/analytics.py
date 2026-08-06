"""
LLM Analytics for SARATHI.

Collects runtime information about LLM requests
for optimization and adaptive routing.
"""

from datetime import datetime


class LLMAnalytics:
    """
    Stores runtime analytics for LLM requests.
    """

    def __init__(self):

        self.requests = []

    def log_request(
        self,
        provider,
        model,
        success,
        latency=None,
        cost=None,
        feedback=None
    ):

        self.requests.append(
            {
                "timestamp": datetime.now(),
                "provider": provider,
                "model": model,
                "success": success,
                "latency": latency,
                "cost": cost,
                "feedback": feedback
            }
        )

    def get_requests(self):

        return self.requests

    def request_count(self):

        return len(self.requests)

    def add_feedback(
        self,
        index,
        feedback
    ):

        if 0 <= index < len(self.requests):

            self.requests[index]["feedback"] = feedback

    def average_latency(self, provider):

        

        values = [
            request["latency"]
            for request in self.requests
            if request["provider"] == provider
            and request["latency"] is not None
        ]

        if not values:
            return None

        #print(self.requests)

        return sum(values) / len(values)

    def success_rate(self, provider):

        requests = [
            request
            for request in self.requests
            if request["provider"] == provider
        ]

        if not requests:
            return 1.0

        successes = sum(
            request["success"]
            for request in requests
        )

        return successes / len(requests)

    def feedback_score(self, provider):

        feedback = [
            request["feedback"]
            for request in self.requests
            if request["provider"] == provider
            and request["feedback"] is not None
        ]

        if not feedback:
            return 0

        score = 0

        for item in feedback:

            if item == "positive":
                score += 1

            elif item == "negative":
                score -= 1

        return score

    def clear(self):

        self.requests.clear()


analytics = LLMAnalytics()