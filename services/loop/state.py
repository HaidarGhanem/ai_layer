from typing import Any, Annotated, TypedDict
from services.risk.level import RiskLevel
from langgraph.graph.message import add_messages


class LoopState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    tool_results: list[dict[str, Any]]
    answer: str
    selected_tools: list[str]
    risk_action: RiskLevel
    risk_decisions: list[dict[str, Any]]