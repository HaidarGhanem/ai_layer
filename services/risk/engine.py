from services.risk.decision import RiskDecision
from services.risk.level import RiskLevel
from services.risk.policy import RiskPolicy

class RiskEngine:

    def __init__(
        self,
        policy: RiskPolicy
    ):
        self.policy = policy

    def check(self, tool_name: str) -> RiskDecision:
        if self.policy.is_blocked(tool_name):
            return RiskDecision(
                action='reject',
                risk_level=RiskLevel.CRITICAL,
                reason=(
                    f"Tool '{tool_name}' is blocked by policy."
                )
            )
        risk_level = self.policy.get_level(tool_name)
        if risk_level == RiskLevel.LOW:
            return RiskDecision(
                action='allow',
                risk_level=risk_level,
                reason=(
                    f"Tool '{tool_name}' is allowed by policy low risk"
                )
            )
        if risk_level == RiskLevel.HIGH:
                return RiskDecision(
                    action='confirm',
                    risk_level=risk_level,
                    reason=(
                        f"Tool '{tool_name}' is high risk and requires confirmation"
                    )
            )
        if risk_level == RiskLevel.CRITICAL:
                        return RiskDecision(
                            action='confirm',
                            risk_level=risk_level,
                            reason=(
                                f"Tool '{tool_name}' is critical risk and requires explicit confirmation"
                            )
                    )
        return RiskDecision(
                action='confirm',
                risk_level=RiskLevel.MEDIUM,
                reason=(
                    f"Tool '{tool_name}' is medium risk by policy."
                )
            )        