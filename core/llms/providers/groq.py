"""
Groq LLM Provider for SARATHI.

Implements the Groq API using the
standard LLM interface.
"""

import time 
import requests
from core.llms.analytics import analytics
from core.llms.config import config

from core.llms.base import LLM
from core.llms.response import LLMResponse
from core.llms.usage import LLMUsage



class GroqLLM(LLM):
    """
    Groq implementation of the LLM interface.
    """

    name = "groq"

    description = "Groq LLM provider."

    default_model = "llama-3.3-70b-versatile"

    supports_streaming = False

    supports_images = False

    supports_tools = False

    offline = False

    supports_reasoning = True

    priority = 2

    def generate(
        self,
        system_prompt,
        user_prompt="",
        temperature=0,
        model="llama-3.3-70b-versatile",
        stream=False
    ):

        api_key = config.GROQ_API_KEY

        if not api_key:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="GROQ_API_KEY is not configured."
            )

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }

        start_time = time.perf_counter()

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            #print(response.json())

        except requests.RequestException as error:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error=str(error)
            )

        data = response.json()

        content = data["choices"][0]["message"]["content"]

        usage = LLMUsage(
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            total_tokens=data["usage"]["total_tokens"],
            prompt_time=data["usage"]["prompt_time"],
            completion_time=data["usage"]["completion_time"],
            total_time=data["usage"]["total_time"]
        )

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return LLMResponse(
            success=True,
            content=content,
            provider=self.name,
            model=model,
            usage=usage
        )

    def is_available(self):
        return bool(config.GROQ_API_KEY)