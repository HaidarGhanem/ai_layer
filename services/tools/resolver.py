from services.tools.register import ToolRegistry


class ToolResolver:

    def __init__(
        self,
        registry: ToolRegistry,
    ):
        self.registry = registry

    def resolve(self, results):

        tools = []
        seen = set()

        for result in results:

            tool_name = (
                result.node.metadata.get(
                    "tool_name"
                )
            )

            if not tool_name:
                continue

            if tool_name in seen:
                continue

            tool = self.registry.get(
                tool_name
            )

            if tool is None:
                continue

            tools.append(tool)

            seen.add(tool_name)

        return tools