"""
LLM Routing Engine for SARATHI.

Determines which provider should handle
a request.
"""

from core.llms.decision import LLMDecision
from core.llms.connectivity import is_online
from core.llms.analytics import analytics


class LLMRouter:
    """
    Determines the best LLM provider for
    a given request.
    """

    def route(
        self,
        manager,
        context
    ):

        if not is_online():

            print("offline mode activated.")

            context.prefer_offline = True

        providers = self.get_available_providers(
            manager
        )

        providers = self.filter_providers(
            providers,
            context
        )

        if not providers:

            return None

        providers = self.sort_providers(
            providers
        )

        provider = providers[0]

        print(f"Selected Provider: {provider.name}")

        fallbacks = self.build_fallback_chain(
            providers
        )

        return LLMDecision(
            provider=provider.name,
            model=provider.default_model,
            reason="policy_selection",
            fallbacks=fallbacks
        )

    def get_available_providers(self, manager):

        providers = []

        for name in manager.list_providers():

            provider = manager.get(name)

            if provider.is_available():
                providers.append(provider)

        return providers

    def get_provider_capabilities(self, provider):

        return {
            "name": provider.name,
            "default_model": provider.default_model,
            "priority": getattr(provider, "priority", 999),
            "offline": getattr(provider, "offline", False),
            "supports_images": provider.supports_images,
            "supports_streaming": provider.supports_streaming,
            "supports_tools": provider.supports_tools,
            "supports_reasoning": provider.supports_reasoning
        }

    def filter_providers(
        self,
        providers,
        context
    ):

        filtered = []

        for provider in providers:

            if (
                context.requires_images
                and not provider.supports_images
            ):
                continue

            if (
                context.requires_tools
                and not provider.supports_tools
            ):
                continue

            if (
                context.requires_reasoning
                and not provider.supports_reasoning
            ):
                continue

            if (
                context.prefer_streaming
                and not provider.supports_streaming
            ):
                continue

            if (
                context.prefer_offline
                and not provider.offline
            ):
                continue

            filtered.append(provider)

        return filtered

    def sort_providers(
        self,
        providers
    ):

        for provider in providers:
            print(
                f"{provider.name}: {self.calculate_provider_score(provider)}"
            )

        providers.sort(
            key=self.calculate_provider_score,
            reverse=True
        )

        return providers

    def build_fallback_chain(
        self,
        providers
    ):

        providers = self.sort_providers(
            providers
        )

        return [
            provider.name
            for provider in providers
        ]

    def calculate_provider_score(
        self,
        provider
    ):
        """
        Calculates an adaptive score for a provider based on
        priority, latency, success rate, and user feedback.
        """

        # Base score from manual priority
        score = provider.priority * 10

        # Reliability
        score += analytics.success_rate(provider.name) * 50

        # User Satisfaction
        score += analytics.feedback_score(provider.name) * 20

        # Performance
        latency = analytics.average_latency(provider.name)
        if latency is not None:
            score -= latency / 200

        print(
            provider.name,
            analytics.average_latency(provider.name)
        )

        return score


router = LLMRouter()