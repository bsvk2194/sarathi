from core.tools.base import Tool
from core.tools.registry import registry


class TestTool(Tool):

    name = "test"

    description = "Simple testing tool."

    def execute(self, **kwargs):
        return "Hello from TestTool"


registry.register(TestTool())

print(registry.list_tools())
print(registry.get("test").execute())