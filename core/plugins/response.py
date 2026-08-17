"""
Plugin Response for SARATHI.
"""

from dataclasses import dataclass, field


@dataclass
class PluginResponse:
    """
    Standard response returned by plugins.
    """

    success: bool

    plugin: str

    action: str

    result: object = None

    error: str | None = None

    metadata: dict = field(default_factory=dict)