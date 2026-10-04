from dataclasses import dataclass


@dataclass
class ToolIndexState:

    tool_id: str

    fingerprint: str

    indexed_fingerprint: str | None = None

    version: int = 1