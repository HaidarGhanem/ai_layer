from typing import Any, Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class LoopState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    tool_results: list[dict[str, Any]]
    answer: str
    selected_tools: list[str]
    risk_action: Literal["allow", "confirm", "reject"] | None
    risk_decisions: list[dict[str, Any]]
