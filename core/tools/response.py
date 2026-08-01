"""
Tool Response model for SARATHI.

Defines the standardized response object
returned by every tool.
"""

class ToolResponse:
    """
    Standard response returned by every tool.
    """

    def __init__(
        self,
        success=True,
        message="",
        data=None
    ):
        self.success = success
        self.message = message
        self.data = data

    def __repr__(self):
        return (
            "ToolResponse("
            f"success={self.success}, "
            f"message='{self.message}', "
            f"data={self.data}"
            ")"
        )