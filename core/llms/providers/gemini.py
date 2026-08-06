"""
Gemini LLM Provider for SARATHI.

Implements the Gemini REST API using the
standard LLM interface.
"""

import requests

from core.llms.base import LLM
from core.llms.config import config
from core.llms.response import LLMResponse
from core.llms.usage import LLMUsage


class GeminiLLM(LLM):
    """
    Gemini implementation of the LLM interface.
    """

    name = "gemini"

    description = "Google Gemini LLM provider."

    default_model = "gemini-3.6-flash"

    supports_streaming = False

    supports_images = True

    supports_tools = False

    offline = False

    supports_reasoning = True

    priority = 3

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

        api_key = config.GEMINI_API_KEY

        if not api_key:

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="GEMINI_API_KEY is not configured."
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text":
                            f"{system_prompt}\n\n{user_prompt}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

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
            prompt_tokens=data["usageMetadata"]["promptTokenCount"],
            completion_tokens=data["usageMetadata"]["candidatesTokenCount"],
            total_tokens=data["usageMetadata"]["totalTokenCount"]
        )

        #print(data)

        try:

            content = (
                data["candidates"][0]
                ["content"]["parts"][0]["text"]
                .strip()
            )

        except (KeyError, IndexError):

            return LLMResponse(
                success=False,
                provider=self.name,
                model=model,
                error="Unexpected response from Gemini."
            )

        return LLMResponse(
            success=True,
            content=content,
            provider=self.name,
            model=model,
            usage=usage
        )

    def is_available(self):
        return bool(config.GEMINI_API_KEY)