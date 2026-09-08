"""Password-length validation: bcrypt truncates by bytes, not characters."""
import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest


def _register(password: str) -> RegisterRequest:
    return RegisterRequest(username="tester", email="t@example.com", password=password)


def test_72_byte_ascii_password_accepted():
    _register("a" * 72)  # must not raise


def test_73_byte_ascii_password_rejected():
    with pytest.raises(ValidationError):
        _register("a" * 73)


def test_72_char_password_with_emoji_exceeds_72_bytes_and_is_rejected():
    # 71 ascii chars + 1 four-byte emoji = 72 chars, 75 bytes
    password = "a" * 71 + "\U0001F600"
    assert len(password) == 72
    assert len(password.encode("utf-8")) == 75
    with pytest.raises(ValidationError):
        _register(password)
