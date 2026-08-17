"""
Persistent storage for SARATHI accounts and plugin bindings.
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from core.accounts.account import Account


class AccountStore:

    def __init__(self):

        self.base_path = Path("config")

        self.base_path.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file = (
            self.base_path / "accounts.json"
        )

    def _serialize_account(self, account):

        data = asdict(account)

        if isinstance(
            data.get("created_at"),
            datetime
        ):

            data["created_at"] = (
                data["created_at"].isoformat()
            )

        if isinstance(
            data.get("updated_at"),
            datetime
        ):

            data["updated_at"] = (
                data["updated_at"].isoformat()
            )

        return data

    def save(
        self,
        accounts,
        bindings
    ):

        data = {
            "accounts": [
                self._serialize_account(account)
                for account in accounts.values()
            ],
            "bindings": bindings
        }

        self.file.write_text(
            json.dumps(
                data,
                indent=4
            ),
            encoding="utf-8"
        )

    def load(self):

        if not self.file.exists():

            return [], {}

        try:

            data = json.loads(
                self.file.read_text(
                    encoding="utf-8"
                )
            )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return [], {}

        accounts = []

        for item in data.get(
            "accounts",
            []
        ):

            for field in (
                "created_at",
                "updated_at"
            ):

                if item.get(field):

                    try:

                        item[field] = (
                            datetime.fromisoformat(
                                item[field]
                            )
                        )

                    except ValueError:

                        pass

            accounts.append(
                Account(**item)
            )

        bindings = data.get(
            "bindings",
            {}
        )

        return accounts, bindings


account_store = AccountStore()