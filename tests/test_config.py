import pytest

from src.config import require_env


def test_require_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("EXAMPLE_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="EXAMPLE_SECRET"):
        require_env("EXAMPLE_SECRET")
