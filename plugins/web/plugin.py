"""
Web Plugin for SARATHI.

Provides internal web search and webpage retrieval.
"""

from core.plugins.base import Plugin

from plugins.web.client import (
    web_client
)


class WebPlugin(Plugin):

    id = "web"

    name = "Web Plugin"

    version = "1.0.0"

    description = (
        "Searches the web, retrieves news, "
        "and extracts webpage content."
    )

    author = "SARATHI"

    permissions = [
        "internet"
    ]

    def execute(
        self,
        request
    ):

        if request.action == "search":

            query = request.parameters.get(
                "query"
            )

            if not query:

                raise ValueError(
                    "Search query is required."
                )

            max_results = request.parameters.get(
                "max_results",
                5
            )

            region = request.parameters.get(
                "region",
                "us-en"
            )

            safesearch = request.parameters.get(
                "safesearch",
                "moderate"
            )

            return web_client.search(
                query=query,
                max_results=max_results,
                region=region,
                safesearch=safesearch
            )

        if request.action == "news":

            query = request.parameters.get(
                "query"
            )

            if not query:

                raise ValueError(
                    "News query is required."
                )

            max_results = request.parameters.get(
                "max_results",
                5
            )

            region = request.parameters.get(
                "region",
                "us-en"
            )

            return web_client.news(
                query=query,
                max_results=max_results,
                region=region
            )

        if request.action == "open_url":

            url = request.parameters.get(
                "url"
            )

            if not url:

                raise ValueError(
                    "URL is required."
                )

            return web_client.extract(
                url
            )

        raise ValueError(
            f"Unknown web action: {request.action}"
        )