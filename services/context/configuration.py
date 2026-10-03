from dataclasses import dataclass

@dataclass
class ContextConfiguration:

    max_tokens: int = 8000
    max_history_tokens: int = 4000
    max_retrieved_tokens: int = 2500
    max_tool_tokens: int = 1500