"""
LLM Routing Decision for SARATHI.

Represents the outcome of the routing engine.
"""

from dataclasses import dataclass


@dataclass
class LLMDecision:
    """
    Represents a routing decision made by the
    LLM routing engine.
    """

    provider: str

    model: str

    reason: str

    fallbacks: list[str] | None = None