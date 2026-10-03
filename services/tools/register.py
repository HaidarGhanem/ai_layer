class ToolRegistry:

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def get_all(self):
        return list(
            self._tools.values()
        )

    def has(self, name: str) -> bool:
        return name in self._tools

    def remove(self, name: str):
        return self._tools.pop(
            name,
            None,
        )