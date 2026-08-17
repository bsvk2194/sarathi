"""
Account Manager for SARATHI.

Responsible for managing connected plugin accounts.
"""

from core.accounts.account import Account
from core.accounts.credential_store import credential_store
from core.accounts.account_store import (
    account_store
)


class AccountManager:

    def __init__(self):

        self.accounts = {}

        self.providers = {}

        self.bindings = {}

        self._load()

    def register_provider(
        self,
        provider
    ):
        """
        Register an authentication provider.
        """

        if not provider.provider_id:

            raise ValueError(
                "Authentication provider must "
                "have a provider_id."
            )

        self.providers[
            provider.provider_id
        ] = provider

    def get_provider(
        self,
        provider_id
    ):

        return self.providers.get(
            provider_id
        )

    def add_account(
        self,
        account,
        credentials=None
    ):
        """
        Add an account and optionally store
        its credentials.
        """

        if not isinstance(
            account,
            Account
        ):

            raise TypeError(
                "Only Account instances "
                "can be added."
            )

        self.accounts[
            account.account_id
        ] = account

        if credentials is not None:

            credential_store.save(
                account.account_id,
                credentials
            )

        self._save()

    def get_account(
        self,
        account_id
    ):

        return self.accounts.get(
            account_id
        )

    def list_accounts(
        self,
        plugin_id=None
    ):
        """
        List all accounts, optionally filtered
        by plugin.
        """

        if plugin_id is None:

            return list(
                self.accounts.values()
            )

        return [
            account
            for account
            in self.accounts.values()
            if account.plugin_id == plugin_id
        ]

    def has_account(
        self,
        account_id
    ):

        return account_id in self.accounts

    def bind_account(
        self,
        plugin_id,
        account_id
    ):
        """
        Bind a connected account to a plugin.
        """

        account = self.get_account(
            account_id
        )

        if account is None:

            raise ValueError(
                f"Account '{account_id}' not found."
            )

        if not account.is_connected():

            raise RuntimeError(
                f"Account '{account_id}' is not connected."
            )

        if not hasattr(
            self,
            "bindings"
        ):

            self.bindings = {}

        if plugin_id not in self.bindings:

            self.bindings[
                plugin_id
            ] = []

        if account_id not in self.bindings[
            plugin_id
        ]:

            self.bindings[
                plugin_id
            ].append(account_id)

        self._save()

    def unbind_account(
        self,
        plugin_id,
        account_id
    ):
        """
        Remove an account binding from a plugin.
        """

        if not hasattr(
            self,
            "bindings"
        ):

            return

        accounts = self.bindings.get(
            plugin_id,
            []
        )

        if account_id in accounts:

            accounts.remove(
                account_id
            )

        if not accounts:

            self.bindings.pop(
                plugin_id,
                None
            )

        self._save()

    def get_bound_accounts(
        self,
        plugin_id
    ):
        """
        Return Account objects bound to a plugin.
        """

        if not hasattr(
            self,
            "bindings"
        ):

            return []

        account_ids = self.bindings.get(
            plugin_id,
            []
        )

        return [
            self.get_account(account_id)
            for account_id in account_ids
            if self.get_account(account_id)
        ]

    def get_bound_account(
        self,
        plugin_id,
        account_id=None
    ):
        """
        Resolve an account for a plugin.

        If account_id is supplied, verify that it is
        bound to the plugin.

        If no account_id is supplied, return the
        first bound account.
        """

        accounts = self.get_bound_accounts(
            plugin_id
        )

        if account_id is not None:

            for account in accounts:

                if account.account_id == account_id:

                    return account

            raise ValueError(
                f"Account '{account_id}' is not "
                f"bound to plugin '{plugin_id}'."
            )

        if accounts:

            return accounts[0]

        return None

    def list_bindings(self):
        """
        Return all plugin/account bindings.
        """

        if not hasattr(
            self,
            "bindings"
        ):

            return {}

        return {
            plugin_id: list(account_ids)
            for plugin_id, account_ids
            in self.bindings.items()
        }

    def disconnect(
        self,
        account_id
    ):
        """
        Disconnect an account and remove
        its stored credentials.
        """

        account = self.get_account(
            account_id
        )

        if account is None:

            return False

        account.disconnect()

        credential_store.delete(
            account_id
        )

        self._save()

        return True

    def remove_account(
        self,
        account_id
    ):
        """
        Completely remove an account.
        """

        self.disconnect(
            account_id
        )

        self.accounts.pop(
            account_id,
            None
        )

    def get_credentials(
        self,
        account_id
    ):

        return credential_store.load(
            account_id
        )

    def _save(self):

        account_store.save(
            self.accounts,
            self.bindings
        )


    def _load(self):

        accounts, bindings = (
            account_store.load()
        )

        self.accounts = {
            account.account_id: account
            for account in accounts
        }

        self.bindings = bindings


account_manager = AccountManager()