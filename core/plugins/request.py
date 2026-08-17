"""
Plugin Request for SARATHI.
"""

from dataclasses import dataclass, field


@dataclass
class PluginRequest:
    """
    Standard request object passed to plugins.
    """

    plugin_id: str

    action: str

    parameters: dict = field(default_factory=dict)

    user: str | None = None

    metadata: dict = field(default_factory=dict)