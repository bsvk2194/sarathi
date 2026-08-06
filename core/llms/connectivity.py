"""
Connectivity utilities for SARATHI.

Provides functions to detect internet connectivity
for intelligent LLM routing.
"""

import requests


CONNECTIVITY_CHECK_URL = "https://www.google.com"


def is_online(timeout=3):
    """
    Returns True if an internet connection
    is available.
    """

    try:

        requests.get(
            CONNECTIVITY_CHECK_URL,
            timeout=timeout
        )

        return True

    except requests.RequestException:

        return False