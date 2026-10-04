from services.observability.langsmith import configure_langsmith


def enable_tracing_from_environment():
    """Configure LangSmith tracing once at application startup."""
    return configure_langsmith()
