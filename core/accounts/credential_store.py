"""
Credential Store for SARATHI.

Responsible for persistent plugin credentials.
"""

import json
from pathlib import Path


class CredentialStore:

    def __init__(self, storage_path=None):

        if storage_path is None:

            storage_path = (
                Path(__file__).parent
                / "credentials.json"
            )

        self.storage_path = Path(
            storage_path
        )

        self._credentials = {}

        self._load()

    def _load(self):

        if not self.storage_path.exists():

            self._credentials = {}

            return

        try:

            with open(
                self.storage_path,
                "r",
                encoding="utf-8"
            ) as file:

                self._credentials = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            self._credentials = {}

    def _save(self):

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self._credentials,
                file,
                indent=4
            )

    def save(
        self,
        account_id,
        credentials
    ):

        self._credentials[
            account_id
        ] = credentials

        self._save()

    def load(
        self,
        account_id
    ):

        return self._credentials.get(
            account_id
        )

    def delete(
        self,
        account_id
    ):

        if account_id in self._credentials:

            del self._credentials[
                account_id
            ]

            self._save()

    def exists(
        self,
        account_id
    ):

        return account_id in self._credentials

    def list_accounts(self):

        return list(
            self._credentials.keys()
        )

    def clear(self):

        self._credentials = {}

        self._save()


credential_store = CredentialStore()