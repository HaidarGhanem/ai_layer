import asyncio

from services.errors.exceptions import (
    AIError,
    CheckpointNotFoundError,
    ClarificationRequiredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
    InternalAIError,
    InvalidRequestError,
    LowRouterConfidenceError,
    ProviderError,
    RiskRejectedError,
    ToolExecutionError,
    ToolSelectorRequiredError,
    UnsupportedRouteError,
)


def normalize_exception(exc: Exception) -> AIError:
    """Normalize implementation/provider exceptions into stable Core errors."""

    if isinstance(exc, AIError):
        return exc

    message = str(exc).strip() or exc.__class__.__name__
    lowered = message.lower()
    class_name = exc.__class__.__name__.lower()
    module_name = exc.__class__.__module__.lower()

    if isinstance(exc, (TimeoutError, asyncio.TimeoutError)) or "timeout" in class_name or "timed out" in lowered:
        return DependencyTimeoutError(details=message)

    if isinstance(exc, ConnectionError) or "connectionerror" in class_name or "connecterror" in class_name:
        return DependencyUnavailableError(details=message)

    if "thread_id is required" in lowered or "thread_id is required when" in lowered:
        return InvalidRequestError(message)

    if "clarification is required" in lowered:
        return ClarificationRequiredError()

    if "router confidence is too low" in lowered:
        return LowRouterConfidenceError()

    if "tool selector is required" in lowered:
        return ToolSelectorRequiredError()

    if "route '" in lowered and "not implemented yet" in lowered:
        return UnsupportedRouteError(message)

    if "rejected by risk policy" in lowered or "requested action was rejected" in lowered:
        return RiskRejectedError(message)

    if "checkpoint" in lowered and any(
        word in lowered for word in ("not found", "missing", "resume")
    ):
        return CheckpointNotFoundError(details=message)

    if "ratelimit" in class_name or "rate limit" in lowered or "too many requests" in lowered:
        return ProviderError(
            "The model provider rate limit was reached.",
            details=message,
        )

    if any(
        token in class_name
        for token in (
            "authentication",
            "unauthorized",
            "permission",
        )
    ):
        return ProviderError(
            "The model provider rejected the request credentials.",
            details=message,
        )

    if any(
        token in class_name
        for token in ("toolexception", "toolerror")
    ) or (module_name.startswith("langchain") and "tool" in class_name):
        return ToolExecutionError(details=message)

    if class_name in {"apierror", "badrequesterror"} or "invalidrequesterror" in class_name:
        return ProviderError(details=message)

    return InternalAIError(details=message)
