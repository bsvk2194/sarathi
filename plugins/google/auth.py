"""
Google OAuth Authentication for SARATHI.
"""
import google.auth
import googleapiclient
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleAuth:

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar"
    ]

    def __init__(self):

        self.base_path = Path(__file__).parent

        self.credentials_file = (
            self.base_path / "credentials.json"
        )

        self.token_file = (
            self.base_path / "token.json"
        )

    def authenticate(self):

        creds = None

        if self.token_file.exists():

            creds = Credentials.from_authorized_user_file(
                str(self.token_file),
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

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                self.SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        self.token_file.write_text(
            creds.to_json()
        )

        return creds


google_auth = GoogleAuth()