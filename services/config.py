import os

from dotenv import load_dotenv


load_dotenv()


def get_env(name: str) -> str | None:
    return os.getenv(name)


def get_env_required(name: str) -> str:
    value = get_env(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable '{name}' is missing."
        )
    return value.strip()


def get_env_bool(name: str, default: bool = False) -> bool:
    value = get_env(name)
    if value is None or not value.strip():
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    raise RuntimeError(
        f"Environment variable '{name}' must be boolean, got '{value}'."
    )


def get_env_int(name: str, default: int) -> int:
    value = get_env(name)
    if value is None or not value.strip():
        return default

    try:
        return int(value.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable '{name}' must be an integer, got '{value}'."
        ) from exc


def get_env_float(name: str, default: float) -> float:
    value = get_env(name)
    if value is None or not value.strip():
        return default

    try:
        return float(value.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable '{name}' must be a number, got '{value}'."
        ) from exc
