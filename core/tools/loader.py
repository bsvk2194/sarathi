import inspect
import importlib
import pkgutil

import core.tools as tools_package

from core.tools.base import Tool
from core.tools.registry import registry

"""
Tool Loader for SARATHI.

Automatically discovers and registers available
tools with the Tool Registry.
"""


def load_tools():

    for _, module_name, _ in pkgutil.iter_modules(
        tools_package.__path__
    ):

        module = importlib.import_module(
            f"core.tools.{module_name}"
        )

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass
        ):

            if (
                issubclass(obj, Tool)
                and obj is not Tool
            ):

                registry.register(obj())