"""
YouTube Music Plugin for SARATHI.
"""

from core.plugins.base import Plugin
from plugins.ytmusic.ytmusic_api import ytmusic_client


class YouTubeMusicPlugin(Plugin):

    id = "ytmusic"

    name = "YouTube Music Plugin"

    version = "1.0.0"

    description = (
        "Provides YouTube Music search "
        "and music information."
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

            limit = request.parameters.get(
                "limit",
                5
            )

            return ytmusic_client.search(
                query,
                limit
            )

        if request.action == "get_song":

            video_id = request.parameters.get(
                "video_id"
            )

            if not video_id:

                raise ValueError(
                    "video_id is required."
                )

            return ytmusic_client.get_song(
                video_id
            )

        if request.action == "get_artist":

            artist_id = request.parameters.get(
                "artist_id"
            )

            if not artist_id:

                raise ValueError(
                    "artist_id is required."
                )

            return ytmusic_client.get_artist(
                artist_id
            )

        raise ValueError(
            f"Unknown YouTube Music action: "
            f"{request.action}"
        )