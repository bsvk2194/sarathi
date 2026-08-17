"""
Plugin Manifest for SARATHI.
"""

from dataclasses import dataclass


@dataclass
class PluginManifest:
    """
    Represents a plugin manifest.
    """

    id: str

    name: str

    version: str

    author: str

    description: str

    entry: str

    plugin_class: str

    permissions: list[str]

    dependencies: list[str]