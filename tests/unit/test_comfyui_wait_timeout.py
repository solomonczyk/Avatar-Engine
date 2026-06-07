from __future__ import annotations

import httpx

import pytest

from avatar_engine.integrations.comfyui.client import ComfyUITimeout, HttpComfyUIClient


class DummyResponse:
    status_code = 200
    is_success = True

    def json(self) -> object:
        return {}

    def raise_for_status(self) -> None:
        return None


def test_wait_timeout_does_not_submit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"get": 0, "post": 0}

    def fake_get(*args, **kwargs):
        calls["get"] += 1
        return DummyResponse()

    def fake_post(*args, **kwargs):
        calls["post"] += 1
        return DummyResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(ComfyUITimeout):
        HttpComfyUIClient("http://test").wait_for_completion("abc", timeout_seconds=0.01, poll_interval=0.001)

    assert calls["get"] >= 1
    assert calls["post"] == 0
