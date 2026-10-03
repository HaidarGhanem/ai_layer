from services.risk.level import RiskLevel
from services.risk.policy import RiskPolicy
from services.risk.engine import RiskEngine


policy = RiskPolicy(
    tool_levels={
        "calculate": RiskLevel.LOW,
        "get_current_time": RiskLevel.LOW,
        "search_customer": RiskLevel.MEDIUM,
        "update_customer": RiskLevel.HIGH,
        "delete_customer": RiskLevel.CRITICAL,
    },
    blocked_tools={
        "dangerous_tool",
    },
)


risk_engine = RiskEngine(
    policy=policy
)


tests = [
    "calculate",
    "get_current_time",
    "search_customer",
    "update_customer",
    "delete_customer",
    "unknown_tool",
    "dangerous_tool",
]


for tool_name in tests:

    result = risk_engine.check(
        tool_name
    )

    print(
        "\n--------------------------------"
    )

    print(
        "TOOL:",
        tool_name
    )

    print(
        "ACTION:",
        result.action
    )

    print(
        "RISK:",
        result.risk_level
    )

    print(
        "REASON:",
        result.reason
    )