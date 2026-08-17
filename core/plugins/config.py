"""
Plugin Configuration Model for SARATHI.
"""

from dataclasses import dataclass, field


@dataclass
class PluginConfig:
    """
    Represents the configuration for a plugin.
    """

    plugin_id: str

    enabled: bool = True

    settings: dict = field(default_factory=dict)