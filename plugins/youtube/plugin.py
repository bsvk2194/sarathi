"""
YouTube Plugin for SARATHI.
"""

from core.plugins.base import Plugin
from plugins.youtube.youtube_api import youtube_client


class YouTubePlugin(Plugin):

    id = "youtube"

    name = "YouTube Plugin"

    version = "1.0.0"

    description = (
        "Provides YouTube search and video information."
    )

    permissions = [
        "internet"
    ]

    def execute(self, request):

        if request.action == "search":

            query = request.parameters.get(
                "query"
            )

            if not query:

                raise ValueError(
                    "query is required."
                )

            max_results = request.parameters.get(
                "max_results",
                5
            )

            return youtube_client.search(
                query,
                max_results
            )

        if request.action == "get_video":

            video_id = request.parameters.get(
                "video_id"
            )

            if not video_id:

                raise ValueError(
                    "video_id is required."
                )

            return youtube_client.get_video(
                video_id
            )

        raise ValueError(
            f"Unknown YouTube action: {request.action}"
        )