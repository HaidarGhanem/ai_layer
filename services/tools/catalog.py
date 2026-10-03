from services.tools.definition import ToolDefinition

class ToolCatalog:
    def __init__(self):
        self._definition: dict[
            str,
            ToolDefinition
        ] = {}

    def add(self, definition: ToolDefinition) -> None :
        self._definition[definition.name] = definition

    def get(self, name: str) -> ToolDefinition | None :
        return self._definition.get(name)

    def get_all(self) -> list[ToolDefinition] :
        return list(self._definition.values())
