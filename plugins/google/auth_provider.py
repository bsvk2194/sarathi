"""
Google Authentication Provider for SARATHI.
"""

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from core.accounts.auth_provider import AuthProvider
from core.accounts.credential_store import credential_store


class GoogleAuthProvider(AuthProvider):

    provider_id = "google"

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar"
    ]

    def __init__(self):

        self.base_path = Path(__file__).parent

        self.credentials_file = (
            self.base_path / "credentials.json"
        )

    def authenticate(
        self,
        account_id
    ):
        """
        Authenticate a Google account.

        Existing credentials for the account are reused.
        Otherwise, Google OAuth login is started.
        """

        stored_credentials = credential_store.load(
            account_id
        )

        creds = None

        if stored_credentials:

            creds = Credentials.from_authorized_user_info(
                stored_credentials,
                self.SCOPES
            )

        if creds and creds.valid:

            return creds

        if (
            creds
            and creds.expired
            and creds.refresh_token
        ):

            creds.refresh(Request())

            credential_store.save(
                account_id,
                json.loads(
                    creds.to_json()
                )
            )

            return creds

        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.credentials_file),
            self.SCOPES
        )

        creds = flow.run_local_server(
            port=0
        )

        credential_store.save(
            account_id,
            json.loads(
                creds.to_json()
            )
        )

        return creds

    def refresh(
        self,
        credentials
    ):
        """
        Refresh Google credentials.
        """

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):

            credentials.refresh(
                Request()
            )

        return credentials

    def disconnect(
        self,
        credentials
    ):
        """
        Revoke Google credentials.
        """

        if credentials is None:

            return

        try:

            credentials.revoke(
                Request()
            )

        except Exception:

            pass

    def is_authenticated(
        self,
        credentials
    ):
        """
        Check whether Google credentials are valid.
        """

        if credentials is None:

            return False

        if credentials.valid:

            return True

        if (
            credentials.expired
            and credentials.refresh_token
        ):

            try:

                credentials.refresh(
                    Request()
                )

                return credentials.valid

            except Exception:

                return False

        return False


google_auth_provider = GoogleAuthProvider()