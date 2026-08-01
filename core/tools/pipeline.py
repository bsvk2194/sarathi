from core.tools.router import router
from core.tools.executor import executor
from core.tools.response import ToolResponse


"""
Tool Pipeline for SARATHI.

Coordinates routing, execution, and response
aggregation for every tool request.
"""

class ToolPipeline:
    """
    Coordinates the complete tool execution pipeline.
    """

    def handle(self, user_input, *args, **kwargs):

        decisions = router.route(user_input)

        if not decisions:
            return ToolResponse(
                success=False,
                message="No suitable tool found.",
                data=None
            )

        tool_queue = []

        for decision in decisions:
            tool_queue.append(decision)

        responses = []

        for decision in tool_queue:

            try:

                response = executor.execute(
                    decision,
                    *args,
                    **kwargs
                )

            except Exception as e:

                response = ToolResponse(
                    success=False,
                    message=f"{decision.tool} failed: {e}",
                    data=None
                )

            responses.append(response)

        messages = []

        for response in responses:

            messages.append(response.message)

        combined_message = "\n".join(messages)

        return ToolResponse(
            success=True,
            message=combined_message,
            data=responses
        )


pipeline = ToolPipeline()