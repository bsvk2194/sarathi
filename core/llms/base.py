"""
Base LLM definitions for SARATHI.

Defines the common interface that every
LLM provider must implement.
"""


class LLM:
    """
    Base class for all LLM providers.
    """

    name = ""

    description = ""

    def generate(
        self,
        system_prompt,
        user_prompt="",
        temperature=0,
        model=None,
        stream=False
    ):
        """
        Generate a response from the LLM.
        """

        raise NotImplementedError(
            "LLM providers must implement generate()."
        )

    def is_available(self):
        return True