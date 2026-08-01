"""
Tool Registry for SARATHI.

Maintains the collection of all registered
tool instances available to the system.
"""

from core.tools.base import Tool


class ToolRegistry:
    """
    Registry that manages all available tools.
    """

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        """
        Register a new tool.
        """

        if not isinstance(tool, Tool):
            raise TypeError(
                "Only Tool subclasses can be registered."
            )

        if not tool.name:
            raise ValueError(
                "Tool must have a name."
            )

        if not tool.description:
            raise ValueError(
                "Tool must have a description."
            )

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(self, name):
        """
        Retrieve a registered tool by name.
        """
        return self._tools.get(name)

    def list_tools(self):
        """
        Return a list of registered tool names.
        """
        return list(self._tools.keys())


# Global registry instance
registry = ToolRegistry()