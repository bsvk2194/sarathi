"""
Claude LLM Provider for SARATHI.

Implements the Anthropic Claude REST API using the
standard LLM interface.
"""

import requests

from core.llms.base import LLM
from core.llms.config import config
from core.llms.response import LLMResponse


class ClaudeLLM(LLM):
    """
    Anthropic Claude implementation of the
    standard LLM interface.
    """

    name = "claude"

    description = "Anthropic Claude LLM provider."

    default_model = "claude-3-5-sonnet-latest"

    supports_streaming = False

    supports_images = True

    supports_tools = False

    offline = False
    
    supports_reasoning = True
    
    priority = 4

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

        api_key = config.CLAUDE_API_KEY

        if not api_key:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="CLAUDE_API_KEY is not configured."
            )

        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 1024,
            "stream": stream
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

        except requests.RequestException as error:

            #print(response.text)

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error=str(error)
            )

        data = response.json()

        try:

            content = (
                data["content"][0]["text"]
                .strip()
            )

        except (KeyError, IndexError):

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="Unexpected response from Claude."
            )

        return LLMResponse(
            success=True,
            content=content,
            provider=self.name,
            model=model
        )

    def is_available(self):
        return False