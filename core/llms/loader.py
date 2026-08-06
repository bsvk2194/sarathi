"""
LLM Loader for SARATHI.

Automatically discovers and registers
available LLM providers.
"""

import inspect
import pkgutil
import importlib

from core.llms.base import LLM
from core.llms.registry import registry
import core.llms.providers


def load_llms():
    """
    Discover and register all LLM providers.
    """

    for _, module_name, _ in pkgutil.iter_modules(core.llms.providers.__path__):

        if module_name in (
            "base",
            "registry",
            "manager",
            "response",
            "loader"
        ):
            continue

        module = importlib.import_module(
            f"core.llms.providers.{module_name}"
        )

        for _, obj in inspect.getmembers(module, inspect.isclass):

            if (
                issubclass(obj, LLM)
                and obj is not LLM
            ):

                registry.register(obj())