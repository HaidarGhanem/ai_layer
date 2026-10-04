import os
from dataclasses import dataclass
from typing import Any

from services.config import get_env, get_env_bool


@dataclass(frozen=True)
class LangSmithConfiguration:
    enabled: bool = False
    api_key: str | None = None
    project: str = "ai-layer-v1"
    endpoint: str = "https://api.smith.langchain.com"

    @classmethod
    def from_env(cls) -> "LangSmithConfiguration":
        api_key = (
            get_env("LANGSMITH_API_KEY")
            or get_env("LANGCHAIN_API_KEY")
        )
        enabled = get_env_bool(
            "LANGSMITH_ENABLED",
            default=bool(api_key),
        )

        return cls(
            enabled=enabled,
            api_key=api_key,
            project=(
                get_env("LANGSMITH_PROJECT")
                or get_env("LANGCHAIN_PROJECT")
                or "ai-layer-v1"
            ),
            endpoint=(
                get_env("LANGSMITH_ENDPOINT")
                or get_env("LANGCHAIN_ENDPOINT")
                or "https://api.smith.langchain.com"
            ),
        )


def configure_langsmith(
    configuration: LangSmithConfiguration | None = None,
) -> LangSmithConfiguration:
    configuration = (
        configuration
        or LangSmithConfiguration.from_env()
    )

    if configuration.enabled and not configuration.api_key:
        raise RuntimeError(
            "LANGSMITH_ENABLED=true requires LANGSMITH_API_KEY."
        )

    if not configuration.enabled:
        return configuration

    os.environ["LANGSMITH_API_KEY"] = configuration.api_key or ""
    os.environ["LANGSMITH_ENDPOINT"] = configuration.endpoint
    os.environ["LANGSMITH_PROJECT"] = configuration.project
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_TRACING_V2"] = "true"

    # Compatibility aliases for code/integrations still reading the
    # historical LANGCHAIN_* environment variable names.
    os.environ["LANGCHAIN_API_KEY"] = configuration.api_key or ""
    os.environ["LANGCHAIN_ENDPOINT"] = configuration.endpoint
    os.environ["LANGCHAIN_PROJECT"] = configuration.project

    return configuration


def get_langsmith_status() -> dict[str, Any]:
    configuration = LangSmithConfiguration.from_env()
    return {
        "enabled": configuration.enabled and bool(configuration.api_key),
        "project": (
            configuration.project
            if configuration.enabled
            else None
        ),
    }


def get_langsmith_client():
    configuration = LangSmithConfiguration.from_env()

    if not configuration.enabled or not configuration.api_key:
        return None

    from langsmith import Client

    return Client(
        api_url=configuration.endpoint,
        api_key=configuration.api_key,
    )
