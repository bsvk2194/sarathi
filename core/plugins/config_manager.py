"""
Plugin Configuration Manager.
"""

from dataclasses import asdict
from pathlib import Path

from core.plugins.config import PluginConfig
from core.plugins.settings import DEFAULT_SETTINGS
from core.plugins.utils import (
    CONFIG_DIRECTORY,
    ensure_directory,
    load_json,
    save_json
)


class PluginConfigManager:

    def __init__(self):

        ensure_directory()

    def config_path(
        self,
        plugin_id
    ):

        return CONFIG_DIRECTORY / f"{plugin_id}.json"

    def create(
        self,
        plugin_id
    ):

        config = PluginConfig(

            plugin_id=plugin_id,

            enabled=True,

            settings=DEFAULT_SETTINGS.get(
                plugin_id,
                {}
            ).copy()
        )

        self.save(config)

        return config

    def save(
        self,
        config
    ):

        save_json(
            self.config_path(
                config.plugin_id
            ),
            asdict(config)
        )

    def load(
        self,
        plugin_id
    ):

        path = self.config_path(
            plugin_id
        )

        if not path.exists():

            return self.create(
                plugin_id
            )

        data = load_json(path)

        return PluginConfig(**data)

    def get(
        self,
        plugin_id
    ):

        return self.load(
            plugin_id
        )

    def update(
        self,
        plugin_id,
        key,
        value
    ):

        config = self.load(
            plugin_id
        )

        config.settings[key] = value

        self.save(config)

        return config

    def reset(
        self,
        plugin_id
    ):

        return self.create(
            plugin_id
        )


config_manager = PluginConfigManager()