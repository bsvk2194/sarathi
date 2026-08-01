"""
Tool Decision model for SARATHI.

Represents the routing decision produced by
the Tool Router before execution.
"""

class ToolDecision:

    """
    Represents the result of routing a request.
    """

    def __init__(
        self,
        tool=None,
        action=None,
        confidence=1.0,
        source="keyword"
    ):
        self.tool = tool
        self.confidence = confidence
        self.source = source
        self.action = action 

    def __repr__(self):
        return (
            "ToolDecision("
            f"tool='{self.tool}', "
            f"confidence={self.confidence}, "
            f"source='{self.source}', "
            f"action='{self.action}'"
            ")"
        )