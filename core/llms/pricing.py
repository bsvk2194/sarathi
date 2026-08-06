"""
LLM pricing utilities.

Provides estimated request costs based on
provider pricing.
"""


class LLMPricing:

    def estimate_cost(
        self,
        provider,
        usage
    ):

        if usage is None:
            return None

        if provider == "ollama":
            return 0.0

        if provider == "groq":
            return 0.0

        if provider == "gemini":
            return 0.0

        if provider == "claude":
            return None

        if provider == "openai":
            return None

        return None


pricing = LLMPricing()