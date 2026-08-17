from core.plugins.base import Plugin


class HelloPlugin(Plugin):

    id = "hello"

    name = "Hello Plugin"

    version = "1.0.0"

    description = "Example plugin."

    def execute(self, request):

        if request.action == "say_hello":

            return "Hello from the Plugin System!"

        return "Unknown action."