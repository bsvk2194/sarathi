"""
YouTube API client for SARATHI.
"""

import os

from googleapiclient.discovery import build


class YouTubeClient:

    def __init__(self):

        self.api_key = os.getenv(
            "YOUTUBE_API_KEY"
        )

        if not self.api_key:

            raise RuntimeError(
                "YOUTUBE_API_KEY is not configured."
            )

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=self.api_key
        )

    def search(
        self,
        query,
        max_results=5
    ):

        response = (
            self.youtube.search()
            .list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            .execute()
        )

        results = []

        for item in response.get(
            "items",
            []
        ):

            results.append(
                {
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "channel": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"]
                }
            )

        return results

    def get_video(
        self,
        video_id
    ):

        response = (
            self.youtube.videos()
            .list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            .execute()
        )

        items = response.get(
            "items",
            []
        )

        if not items:

            raise ValueError(
                f"YouTube video '{video_id}' not found."
            )

        item = items[0]

        return {
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"],
            "duration": item["contentDetails"]["duration"],
            "views": item["statistics"].get(
                "viewCount"
            ),
            "likes": item["statistics"].get(
                "likeCount"
            )
        }


youtube_client = YouTubeClient()