from services.risk.level import RiskLevel

class RiskPolicy:
    def __init__(
            self, 
            tool_levels: dict[str, RiskLevel] | None = None,
            blocked_tools: set[str] | None = None
        ):
            self.tool_levels = tool_levels or {}
            self.blocked_tools = blocked_tools or set()

    def get_level(self,tool_name: str) -> RiskLevel:
            return self.tool_levels.get(
                   tool_name,
                   RiskLevel.MEDIUM
            )

    def is_blocked(self,tool_name: str) -> bool:
           return tool_name in self.blocked_tools

    