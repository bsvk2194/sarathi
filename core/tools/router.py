"""
Tool Router for SARATHI.

Determines which tool should handle a user
request using keyword and LLM-based routing.
"""


from core.tools.decision import ToolDecision
from core.llm import select_tool

TOOL_KEYWORDS = {
    "memory": [
        "remember",
        "forget",
        "memory"
    ]
}

MEMORY_ACTIONS = {
    "remember": "remember",
    "forget": "forget",
    "search": "search",
    "memory": "search"
}


class ToolRouter:
    """
    Determine which tool and action should handle a request.
    """

    def route(self, text):

        text = text.lower()

        # ----------------------------
        # Determine the action
        # ----------------------------

        action = None

        for keyword, method in MEMORY_ACTIONS.items():
            if keyword in text:
                action = method
                break

        # ----------------------------
        # Keyword-based routing
        # ----------------------------

        for tool, keywords in TOOL_KEYWORDS.items():

            if any(word in text for word in keywords):

                return [ToolDecision(
                    tool=tool,
                    action=action,
                    confidence=1.0,
                    source="keyword"
                )]

        # ----------------------------
        # LLM fallback
        # ----------------------------

        tool = select_tool(
            text,
            list(TOOL_KEYWORDS.keys())
        )

        # Temporary fallback until the LLM returns actions.
        if tool is not None and action is None:
            action = "remember"

        if tool is None:
            return []

        return [ToolDecision(
            tool=tool,
            action=action,
            confidence=0.8,
            source="llm"
        )]


router = ToolRouter()