from dataclasses import dataclass

from services.config import get_env, get_env_bool, get_env_int


@dataclass(frozen=True)
class APIConfiguration:
    service_name: str = "AI Layer"
    version: str = "1.0.0"
    prefix: str = "/v1"
    debug: bool = False
    max_question_chars: int = 10000
    max_session_id_chars: int = 256
    cors_origins: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.prefix.startswith("/"):
            object.__setattr__(self, "prefix", f"/{self.prefix}")
        if self.prefix != "/":
            object.__setattr__(self, "prefix", self.prefix.rstrip("/"))

        if self.max_question_chars < 1:
            raise ValueError("max_question_chars must be positive")
        if self.max_session_id_chars < 1:
            raise ValueError("max_session_id_chars must be positive")

    @classmethod
    def from_env(cls) -> "APIConfiguration":
        origins_raw = get_env("AI_CORS_ORIGINS") or ""
        origins = tuple(
            item.strip()
            for item in origins_raw.split(",")
            if item.strip()
        )

        return cls(
            service_name=get_env("AI_SERVICE_NAME") or "AI Layer",
            version=get_env("AI_VERSION") or "1.0.0",
            prefix=get_env("AI_API_PREFIX") or "/v1",
            debug=get_env_bool("AI_DEBUG", False),
            max_question_chars=get_env_int(
                "AI_MAX_QUESTION_CHARS",
                10000,
            ),
            max_session_id_chars=get_env_int(
                "AI_MAX_SESSION_ID_CHARS",
                256,
            ),
            cors_origins=origins,
        )
