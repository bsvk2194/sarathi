"""
Base Plugin interface for SARATHI.

Every plugin must inherit from this class.
"""


class Plugin:
    """
    Base class for all SARATHI plugins.
    """

    id = ""

    name = ""

    version = "1.0.0"

    description = ""

    author = "SARATHI"

    enabled = True

    permissions = []

    dependencies = []

    def install(self):
        """
        Called when the plugin is installed.
        """
        pass

    def uninstall(self):
        """
        Called when the plugin is removed.
        """
        pass

    def enable(self):
        """
        Enable the plugin.
        """
        self.enabled = True

    def disable(self):
        """
        Disable the plugin.
        """
        self.enabled = False

    def is_enabled(self):
        """
        Returns whether the plugin is enabled.
        """
        return self.enabled

    def execute(self, request):
        """
        Executes the plugin.

        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement execute()."
        )