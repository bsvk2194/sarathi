"""
LLM Registry for SARATHI.

Maintains the collection of all registered
LLM providers available to the system.
"""


class LLMRegistry:
    """
    Stores registered LLM providers.
    """

    def __init__(self):

        self._providers = {}

    def register(self, provider):

        self._providers[provider.name] = provider

    def get(self, name):

        return self._providers.get(name)

    def list_providers(self):

        return list(self._providers.keys())


registry = LLMRegistry()