from services.tools.record import ToolRecord


class ToolRegistry:

    def __init__(self):

        self._tools = {}

    def register(
        self,
        tool,
        definition,
    ) -> ToolRecord:

        record = ToolRecord(
            name=tool.name,
            tool=tool,
            definition=definition,
        )

        self._tools[
            tool.name
        ] = record

        return record

    def get(
        self,
        name: str,
    ):

        record = self._tools.get(
            name
        )

        if record is None:
            return None

        if not record.enabled:
            return None

        return record.tool

    def get_record(
        self,
        name: str,
    ):

        return self._tools.get(
            name
        )

    def get_all(self):

        return [
            record.tool
            for record in self._tools.values()
            if record.enabled
        ]

    def get_all_records(self):

        return list(
            self._tools.values()
        )

    def has(
        self,
        name: str,
    ) -> bool:

        record = self._tools.get(
            name
        )

        return (
            record is not None
            and record.enabled
        )

    def update(
        self,
        tool,
        definition,
    ) -> ToolRecord:

        record = self._tools.get(
            tool.name
        )

        if record is None:

            return self.register(
                tool=tool,
                definition=definition,
            )

        record.tool = tool
        record.definition = definition
        record.version += 1

        return record

    def remove(
        self,
        name: str,
    ):

        return self._tools.pop(
            name,
            None
        )

    def enable(
        self,
        name: str,
    ) -> bool:

        record = self._tools.get(
            name
        )

        if record is None:
            return False

        record.enabled = True

        return True

    def disable(
        self,
        name: str,
    ) -> bool:

        record = self._tools.get(
            name
        )

        if record is None:
            return False

        record.enabled = False

        return True