"""
Web Client for SARATHI.

Provides web search and webpage extraction.
"""

from ddgs import DDGS


class WebClient:

    def __init__(self):

        self.client = DDGS()

    def search(
        self,
        query,
        max_results=5,
        region="us-en",
        safesearch="moderate"
    ):

        return self.client.text(
            query,
            region=region,
            safesearch=safesearch,
            max_results=max_results
        )

    def news(
        self,
        query,
        max_results=5,
        region="us-en"
    ):

        return self.client.news(
            query,
            region=region,
            max_results=max_results
        )

    def extract(
        self,
        url
    ):

        return self.client.extract(
            url
        )


web_client = WebClient()