"""
LLM Configuration for SARATHI.

Loads and provides configuration values
shared across all LLM providers.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """
    Shared configuration for all LLM providers.
    """

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434"
    )


config = LLMConfig()