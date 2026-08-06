"""
LLM Request Context for SARATHI.

Represents the requirements of an LLM request
that will be used by the routing engine.
"""

from dataclasses import dataclass


@dataclass
class LLMContext:
    """
    Describes the requirements of a request.
    """

    requires_images: bool = False

    requires_tools: bool = False

    requires_reasoning: bool = False

    prefer_offline: bool = False

    prefer_streaming: bool = False