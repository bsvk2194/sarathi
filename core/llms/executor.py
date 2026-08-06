"""
LLM Execution Engine for SARATHI.

Responsible for executing requests using the
provider selected by the router.
"""

import time
from core.llms.manager import llms
from core.llms.analytics import analytics
from core.llms.pricing import pricing


class LLMExecutor:
    """
    Executes LLM requests.
    """

    def execute(
        self,
        decision,
        system_prompt,
        user_prompt="",
        temperature=0
    ):

        last_response = None

        for provider_name in decision.fallbacks:

            provider = llms.get(provider_name)

            start_time = time.perf_counter()

            response = provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=decision.model,
                temperature=temperature
            )

            cost = pricing.estimate_cost(
                provider=provider.name,
                usage=response.usage
            )

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

            '''analytics.log_request(
                provider=provider.name,
                model=decision.model,
                success=response.success,
                latency=latency_ms,
                cost=cost
            )'''

            if response.success:

                return response

            last_response = response

        return last_response


executor = LLMExecutor()