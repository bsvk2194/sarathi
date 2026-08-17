"""
Google API Client for SARATHI.

Provides authenticated clients for Google services.
"""

from googleapiclient.discovery import build

from plugins.google.auth_provider import (
    google_auth_provider
)


class GoogleClient:

    def __init__(self):

        self.credentials = {}

    def authenticate(
        self,
        account_id
    ):
        """
        Authenticate a specific Google account.
        """

        credentials = (
            google_auth_provider.authenticate(
                account_id
            )
        )

        self.credentials[
            account_id
        ] = credentials

        return credentials

    def service(
        self,
        service_name,
        version,
        account_id="google_personal"
    ):
        """
        Return an authenticated Google API service
        for a specific account.
        """

        if account_id not in self.credentials:

            self.authenticate(
                account_id
            )

        return build(
            service_name,
            version,
            credentials=self.credentials[
                account_id
            ]
        )


google_client = GoogleClient()