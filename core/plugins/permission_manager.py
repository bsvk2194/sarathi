"""
Permission Manager for SARATHI.
"""

from core.plugins.permissions import Permission


class PermissionManager:

    def __init__(self):

        self.granted = {}

    def grant(
        self,
        plugin_id,
        permission
    ):

        self.granted.setdefault(
            plugin_id,
            set()
        ).add(permission)

    def revoke(
        self,
        plugin_id,
        permission
    ):

        if plugin_id in self.granted:

            self.granted[plugin_id].discard(
                permission
            )

    def has_permission(
        self,
        plugin_id,
        permission
    ):

        return (
            permission
            in self.granted.get(
                plugin_id,
                set()
            )
        )

    def get_permissions(
        self,
        plugin_id
    ):

        return self.granted.get(
            plugin_id,
            set()
        )


permission_manager = PermissionManager()