"""
Usage information returned by an LLM provider.
"""

from dataclasses import dataclass


@dataclass
class LLMUsage:

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    prompt_time: float | None = None

    completion_time: float | None = None

    total_time: float | None = None