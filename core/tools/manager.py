"""
Tool Manager for SARATHI.

Provides centralized access to registered tools
throughout the Tool System.
"""

from core.tools.registry import registry


class ToolManager:
    """
    Central interface for accessing registered tools.
    """

    def get(self, tool_name):
        """
        Retrieve a registered tool by name.
        """
        tool = registry.get(tool_name)

        if tool is None:
            raise ValueError(f"Tool '{tool_name}' is not registered.")

        return tool

    @property
    def memory(self):
        """
        Access the Memory Tool.
        """
        return self.get("memory")


# Global Tool Manager instance
tools = ToolManager()