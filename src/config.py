import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
    def load_dotenv(*_args, **_kwargs):
        return False


load_dotenv()


def require_env(name: str, *, default: str | None = None, allow_empty: bool = False) -> str:
    """Return a required environment variable value or raise a clear error."""
    value = os.getenv(name, default)

    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in your .env file or deployment environment."
        )

    value = str(value).strip()
    if not allow_empty and not value:
        raise RuntimeError(
            f"Environment variable {name} is configured but empty. "
            "Provide a valid value before starting the application."
        )

    return value


def get_db_config() -> dict:
    """Return validated database settings for application and API code."""
    try:
        port = int(require_env("DB_PORT"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be an integer.") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("DB_PORT must be between 1 and 65535.")
    return {
        "host": require_env("DB_HOST"),
        "port": port,
        "user": require_env("DB_USER"),
        "password": require_env("DB_PASSWORD"),
        "database": require_env("DB_NAME"),
    }
