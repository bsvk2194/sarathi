"""
Plugin Manager for SARATHI.

Responsible for managing plugin instances.
"""


from core.plugins.registry import registry
from core.plugins.base import Plugin
from core.plugins.permission_manager import permission_manager


class PluginManager:
    """
    Manages plugin instances.
    """

    def __init__(self):

        self.plugins = {}

        self.installed = set()  

    def load(self, plugin):

        if not isinstance(plugin, Plugin):

            raise TypeError(
                "Only Plugin instances can be loaded."
            )

        self.plugins[plugin.id] = plugin

    def unload(self, plugin_id):

        self.plugins.pop(plugin_id, None)

    def get(self, plugin_id):

        return self.plugins.get(plugin_id)

    def list_plugins(self):

        return list(self.plugins.keys())

    def list(self):

        return list(self.plugins.values())

    def enable(self, plugin_id):

        if not self.is_installed(plugin_id):

            raise RuntimeError(
                "Plugin is not installed."
            )

        plugin = self.get(plugin_id)

        plugin.enable()

    def disable(self, plugin_id):

        if not self.is_installed(plugin_id):

            raise RuntimeError(
                "Plugin is not installed."
            )

        plugin = self.get(plugin_id)

        plugin.disable()

    def clear(self):

        self.plugins.clear()

    def install(self, plugin_id):

        plugin = self.get(plugin_id)

        if plugin is None:

            raise ValueError(
                f"Plugin '{plugin_id}' not found."
            )

        self.installed.add(plugin_id)

        plugin.installed = True

        plugin.install()

    def is_installed(self, plugin_id):

            return plugin_id in self.installed

    def uninstall(self, plugin_id):

        plugin = self.get(plugin_id)

        if plugin is None:

            return

        plugin.uninstall()

        plugin.installed = False

        plugin.enabled = False

        self.installed.discard(plugin_id)

    def update(self, plugin_id):

        plugin = self.get(plugin_id)

        if plugin is None:

            return

        plugin.disable()

        plugin.enable()


    def validate_permission(
        self,
        plugin_id,
        permission
    ):
        """
        Validate that a plugin has a required permission.
        """

        if not permission_manager.has_permission(
            plugin_id,
            permission
        ):

            raise PermissionError(
                f"Plugin '{plugin_id}' does not have '{permission.value}' permission."
            )

    
plugins = PluginManager()