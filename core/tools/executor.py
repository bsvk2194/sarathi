from core.tools.manager import tools
from core.tools.response import ToolResponse

"""
Tool Executor for SARATHI.

Executes tool actions selected by the Tool Router
and returns standardized ToolResponse objects.
"""

class ToolExecutor:

    def get_tool(self, decision):

        if decision.tool is None:
            return None

        return tools.get(decision.tool)

    def execute(self, decision, *args, **kwargs):

        tool = self.get_tool(decision)

        if tool is None:
            return ToolResponse(
                success=False,
                message=f"Tool '{decision.tool}' is not registered.",
                data=None
            )

        method = getattr(tool, decision.action, None)

        if method is None:
            return ToolResponse(
                success=False,
                message=f"Action '{decision.action}' is not supported by '{decision.tool}'.",
                data=None
            )


        response = method(*args, **kwargs)

        return response


executor = ToolExecutor()