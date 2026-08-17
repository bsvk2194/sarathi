"""
Plugin Loader for SARATHI.

Automatically discovers and loads plugins.
"""

import json
import importlib.util
from pathlib import Path

from core.plugins.registry import registry
from core.plugins.manager import plugins


class PluginLoader:

    def __init__(self):

        self.plugin_directory = Path("plugins")

    def load_plugins(self):

        if not self.plugin_directory.exists():

            return

        for folder in self.plugin_directory.iterdir():

            if not folder.is_dir():

                continue

            manifest_path = folder / "plugin.json"

            if not manifest_path.exists():

                continue

            with open(
                manifest_path,
                "r",
                encoding="utf-8"
            ) as file:

                manifest = json.load(file)

            module_path = folder / manifest["entry"]

            spec = importlib.util.spec_from_file_location(
                manifest["id"],
                module_path
            )

            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            plugin_class = getattr(
                module,
                manifest["class"]
            )

            plugin = plugin_class()

            registry.register(plugin)

            plugins.load(plugin)

            plugins.install(plugin.id)

            plugins.enable(plugin.id)



loader = PluginLoader()