from core.tools.base import Tool

"""
Knowledge Service wrappers for SARATHI.

Provides a service layer between the Tool System
and the Knowledge subsystem.
"""


class KnowledgeTool(Tool):

    name = "knowledge"

    description = "Reasons over stored knowledge and memories."

    