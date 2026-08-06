"""
LLM Manager for SARATHI.

Provides centralized access to registered
LLM providers throughout the system.
"""

from core.llms.registry import registry


class LLMManager:
    """
    Centralized interface for accessing
    registered LLM providers.
    """

    def list_providers(self):

        return registry.list_providers()

    def __getattr__(self, name):

        provider = registry.get(name)

        if provider is None:
            raise AttributeError(
                f"No LLM provider named '{name}' is registered."
            )

        return provider


    def get(self, name):

        provider = registry.get(name)

        if provider is None:

            raise ValueError(
                f"No LLM provider named '{name}' is registered."
            )

        return provider

llms = LLMManager()