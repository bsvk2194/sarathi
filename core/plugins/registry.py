"""
Plugin Registry for SARATHI.

Responsible for registering and retrieving plugins.
"""


class PluginRegistry:
    """
    Registry for all available plugins.
    """

    def __init__(self):

        self._plugins = {}

    def register(self, plugin):

        if plugin.id in self._plugins:

            raise ValueError(
                f"Plugin '{plugin.id}' is already registered."
            )

        self._plugins[plugin.id] = plugin

    def unregister(self, plugin_id):
        """
        Remove a plugin from the registry.
        """

        self._plugins.pop(plugin_id, None)

    def get(self, plugin_id):
        """
        Retrieve a plugin by ID.
        """

        return self._plugins.get(plugin_id)

    def list_plugins(self):
        """
        Return a list of registered plugin IDs.
        """

        return list(self._plugins.keys())

    def list(self):
        """
        Return all registered plugin classes.
        """

        return list(self._plugins.values())

    def clear(self):
        """
        Remove every registered plugin.
        """

        self._plugins.clear()


registry = PluginRegistry()