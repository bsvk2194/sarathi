"""
Plugin Runtime for SARATHI.
"""

import time

from core.plugins.manager import plugins
from core.plugins.response import PluginResponse
from core.plugins.analytics import analytics


class PluginExecutor:
    """
    Executes plugins.
    """

    def execute(self, request):

        plugin = plugins.get(request.plugin_id)

        if plugin is None:

            return PluginResponse(
                success=False,
                plugin=request.plugin_id,
                action=request.action,
                error="Plugin not found."
            )

        if not plugin.is_enabled():

            return PluginResponse(
                success=False,
                plugin=request.plugin_id,
                action=request.action,
                error="Plugin is disabled."
            )

        start = time.perf_counter()

        try:

            result = plugin.execute(
                request
            )

            elapsed = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            analytics.log_request(
                plugin.id,
                request.action,
                True,
                elapsed
            )

            return PluginResponse(
                success=True,
                plugin=plugin.id,
                action=request.action,
                result=result
            )

        except Exception as error:

            elapsed = round(
                (time.perf_counter() - start) * 1000,
                2
            )

            analytics.log_request(
                plugin.id,
                request.action,
                False,
                elapsed
            )

            return PluginResponse(
                success=False,
                plugin=plugin.id,
                action=request.action,
                error=str(error)
            )


executor = PluginExecutor()