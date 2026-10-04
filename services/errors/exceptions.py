from typing import Any

from services.errors.codes import ErrorCode


class AIError(Exception):
    """Stable domain error exposed by the AI Core and API layers."""

    def __init__(
        self,
        message: str,
        *,
        code: str | ErrorCode = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Any = None,
    ):
        self.message = str(message)
        self.code = (
            code.value
            if isinstance(code, ErrorCode)
            else str(code)
        )
        self.status_code = int(status_code)
        self.details = details
        super().__init__(self.message)


class InvalidRequestError(AIError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.INVALID_REQUEST,
            status_code=400,
            details=details,
        )


class ClarificationRequiredError(AIError):
    def __init__(self, message: str = "Clarification is required.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.CLARIFICATION_REQUIRED,
            status_code=422,
            details=details,
        )


class LowRouterConfidenceError(AIError):
    def __init__(self, message: str = "Router confidence is too low.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.LOW_ROUTER_CONFIDENCE,
            status_code=422,
            details=details,
        )


class ToolSelectorRequiredError(AIError):
    def __init__(self, message: str = "Tool selector is required for loop route.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.TOOL_SELECTOR_REQUIRED,
            status_code=503,
            details=details,
        )


class UnsupportedRouteError(AIError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.UNSUPPORTED_ROUTE,
            status_code=400,
            details=details,
        )


class RiskRejectedError(AIError):
    def __init__(self, message: str = "The requested action was rejected by the risk policy.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.RISK_REJECTED,
            status_code=403,
            details=details,
        )


class CheckpointNotFoundError(AIError):
    def __init__(self, message: str = "No resumable checkpoint was found for this session.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.CHECKPOINT_NOT_FOUND,
            status_code=409,
            details=details,
        )


class ProviderError(AIError):
    def __init__(self, message: str = "The model provider request failed.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.PROVIDER_ERROR,
            status_code=502,
            details=details,
        )


class ToolExecutionError(AIError):
    def __init__(self, message: str = "Tool execution failed.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.TOOL_EXECUTION_ERROR,
            status_code=502,
            details=details,
        )


class DependencyTimeoutError(AIError):
    def __init__(self, message: str = "An upstream dependency timed out.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.DEPENDENCY_TIMEOUT,
            status_code=504,
            details=details,
        )


class DependencyUnavailableError(AIError):
    def __init__(self, message: str = "An upstream dependency is unavailable.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.DEPENDENCY_UNAVAILABLE,
            status_code=503,
            details=details,
        )


class InternalAIError(AIError):
    def __init__(self, message: str = "Internal AI service error.", details: Any = None):
        super().__init__(
            message,
            code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            details=details,
        )
