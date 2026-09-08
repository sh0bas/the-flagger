"""The rate limiter's dict must not grow forever, and must actually limit."""
import time
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import deps


class FakeRequest(SimpleNamespace):
    """rate_limit() only touches request.client.host."""


def _req(ip: str):
    return FakeRequest(client=SimpleNamespace(host=ip))


@pytest.fixture(autouse=True)
def clean_hits():
    deps._hits.clear()
    yield
    deps._hits.clear()


def test_allows_up_to_the_limit():
    for _ in range(deps._RATE_LIMIT):
        deps.rate_limit(_req("1.2.3.4"))  # must not raise


def test_blocks_over_the_limit():
    for _ in range(deps._RATE_LIMIT):
        deps.rate_limit(_req("1.2.3.4"))
    with pytest.raises(HTTPException) as exc:
        deps.rate_limit(_req("1.2.3.4"))
    assert exc.value.status_code == 429


def test_separate_clients_have_separate_budgets():
    for _ in range(deps._RATE_LIMIT):
        deps.rate_limit(_req("1.1.1.1"))
    deps.rate_limit(_req("2.2.2.2"))  # must not raise, different client


def test_expired_clients_are_evicted_not_kept_forever(monkeypatch):
    t = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: t[0])

    deps.rate_limit(_req("9.9.9.9"))
    assert "9.9.9.9" in deps._hits

    t[0] += deps._RATE_WINDOW_S + 1  # let that client's window fully expire
    deps.rate_limit(_req("8.8.8.8"))  # any call sweeps expired entries

    assert "9.9.9.9" not in deps._hits
    assert "8.8.8.8" in deps._hits
