"""
YouTube Music API client for SARATHI.
"""

from ytmusicapi import YTMusic


class YouTubeMusicClient:

    def __init__(self):

        self.client = YTMusic()

    def search(
        self,
        query,
        limit=5
    ):

        results = self.client.search(
            query,
            filter="songs"
        )

        return results[:limit]

    def get_song(
        self,
        video_id
    ):

        return self.client.get_song(
            video_id
        )

    def get_artist(
        self,
        artist_id
    ):

        return self.client.get_artist(
            artist_id
        )


ytmusic_client = YouTubeMusicClient()