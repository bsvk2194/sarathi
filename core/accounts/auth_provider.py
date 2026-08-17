"""
Authentication Provider Interface for SARATHI.

Defines the common authentication contract that
individual providers must implement.
"""


class AuthProvider:
    """
    Base authentication provider.
    """

    provider_id = ""

    def authenticate(self):
        """
        Authenticate the user and return credentials.

        Must be implemented by subclasses.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "must implement authenticate()."
        )

    def refresh(self, credentials):
        """
        Refresh expired credentials.

        Must be implemented by subclasses.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "must implement refresh()."
        )

    def disconnect(self, credentials):
        """
        Disconnect/revoke an authenticated account.

        Must be implemented by subclasses.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "must implement disconnect()."
        )

    def is_authenticated(self, credentials):
        """
        Check whether credentials are currently valid.

        Must be implemented by subclasses.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "must implement is_authenticated()."
        )