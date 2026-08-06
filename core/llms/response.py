"""
LLM Response model for SARATHI.

Defines the standardized response object
returned by every LLM provider.
"""

from core.llms.usage import LLMUsage


class LLMResponse:
    """
    Standard response returned by every LLM.
    """

    def __init__(
        self,
        success=True,
        content="",
        provider="",
        model="",
        latency=None,
        usage: LLMUsage | None = None,
        error=None
    ):
        self.success = success
        self.content = content
        self.provider = provider
        self.model = model
        self.latency = latency
        self.usage = usage
        self.error = error

    def __repr__(self):
        return (
            "LLMResponse("
            f"success={self.success}, "
            f"provider='{self.provider}', "
            f"model='{self.model}', "
            f"latency={self.latency}, "
            f"usage={self.usage}, "
            f"error={self.error}, "
            f"content='{self.content}'"
            ")"
        )