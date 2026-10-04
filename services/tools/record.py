from dataclasses import dataclass
from typing import Any

from services.tools.definition import ToolDefinition


@dataclass
class ToolRecord:

    name: str

    tool: Any

    definition: ToolDefinition

    version: int = 1

    enabled: bool = True

    fingerprint: str = ""

    indexed_fingerprint: str | None = None