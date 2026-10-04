from services.errors.codes import ErrorCode
from services.errors.exceptions import (
    AIError,
    ClarificationRequiredError,
    DependencyTimeoutError,
    InvalidRequestError,
    LowRouterConfidenceError,
    ProviderError,
    RiskRejectedError,
    ToolSelectorRequiredError,
)
from services.errors.translate import normalize_exception


def assert_error(error, code, status):
    assert isinstance(error, AIError)
    assert error.code == code.value
    assert error.status_code == status


def main():
    assert_error(
        InvalidRequestError("bad"),
        ErrorCode.INVALID_REQUEST,
        400,
    )
    assert_error(
        ClarificationRequiredError(),
        ErrorCode.CLARIFICATION_REQUIRED,
        422,
    )
    assert_error(
        LowRouterConfidenceError(),
        ErrorCode.LOW_ROUTER_CONFIDENCE,
        422,
    )
    assert_error(
        ToolSelectorRequiredError(),
        ErrorCode.TOOL_SELECTOR_REQUIRED,
        503,
    )
    assert_error(
        RiskRejectedError(),
        ErrorCode.RISK_REJECTED,
        403,
    )
    assert_error(
        ProviderError(),
        ErrorCode.PROVIDER_ERROR,
        502,
    )
    assert_error(
        DependencyTimeoutError(),
        ErrorCode.DEPENDENCY_TIMEOUT,
        504,
    )

    assert normalize_exception(
        ValueError("Clarification is required")
    ).code == ErrorCode.CLARIFICATION_REQUIRED.value

    assert normalize_exception(
        ValueError("Router confidence is too low")
    ).code == ErrorCode.LOW_ROUTER_CONFIDENCE.value

    assert normalize_exception(
        ValueError("Tool selector is required for loop route.")
    ).code == ErrorCode.TOOL_SELECTOR_REQUIRED.value

    assert normalize_exception(
        TimeoutError("provider timeout")
    ).code == ErrorCode.DEPENDENCY_TIMEOUT.value

    assert normalize_exception(
        ConnectionError("connection failed")
    ).code == ErrorCode.DEPENDENCY_UNAVAILABLE.value

    assert normalize_exception(
        ValueError("A thread_id is required when the loop uses a checkpointer.")
    ).code == ErrorCode.INVALID_REQUEST.value

    print("=" * 60)
    print("V1 ERROR HANDLING TEST: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
