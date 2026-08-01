"""
Base Tool definitions for SARATHI.

Defines the common interface that every tool
must implement within the Tool System.
"""


class Tool:
    """
    Base class that every SARATHI tool must inherit from.
    """

    name = ""
    description = ""

    def execute(self, **kwargs):
        """
        Execute the tool.

        Every tool must override this method.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement execute()."
        )