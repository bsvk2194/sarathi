"""
Ollama LLM Provider for SARATHI.

Implements the Ollama REST API using the
standard LLM interface.
"""


import time 
import requests

from core.llms.base import LLM
from core.llms.config import config
from core.llms.response import LLMResponse
from core.llms.analytics import analytics
from core.llms.usage import LLMUsage


class OllamaLLM(LLM):
    """
    Ollama implementation of the LLM interface.
    """

    name = "ollama"

    description = "Local Ollama LLM provider."

    default_model = "llama3.2:3b"

    supports_streaming = True

    supports_images = False

    supports_tools = False

    offline = True

    supports_reasoning = True

    priority = 1

    def generate(
        self,
        system_prompt,
        user_prompt="",
        temperature=0,
        model=None,
        stream=False
    ):

        if model is None:
            model = self.default_model

        url = f"{config.OLLAMA_URL}/api/generate"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        start_time = time.perf_counter()

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

        except requests.RequestException as error:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error=str(error)
            )

        data = response.json()

        usage = LLMUsage(
            prompt_tokens=data["prompt_eval_count"],
            completion_tokens=data["eval_count"],
            total_tokens=data["prompt_eval_count"] + data["eval_count"],
            prompt_time=data["prompt_eval_duration"] / 1_000_000_000,
            completion_time=data["eval_duration"] / 1_000_000_000,
            total_time=data["total_duration"] / 1_000_000_000
        )

        #print(data)

        try:

            content = data["response"].strip()

        except KeyError:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="Unexpected response from Ollama."
            )

        return LLMResponse(
            success=True,
            content=content,
            provider=self.name,
            model=model,
            usage=usage
        )

    def is_available(self):
        try:
            requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
            return True
        except requests.RequestException:
            return False