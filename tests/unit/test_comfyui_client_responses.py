from __future__ import annotations

import httpx

import pytest

from avatar_engine.integrations.comfyui.client import ComfyUIMalformedResponse, HttpComfyUIClient


class DummyResponse:
    def __init__(self, payload: object, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> object:
        return self._payload

    def raise_for_status(self) -> None:
        if not self.is_success:
            raise httpx.HTTPStatusError("error", request=httpx.Request("GET", "http://test"), response=httpx.Response(self.status_code))


def test_successful_submit_parses_prompt_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: DummyResponse({"prompt_id": "abc123"}))

    result = HttpComfyUIClient("http://test").submit_workflow({"1": {"inputs": {}, "class_type": "SaveImage"}})

    assert result.prompt_id == "abc123"
    assert result.submitted is True


def test_submit_rejects_malformed_prompt_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: DummyResponse({"prompt_id": ""}))

    with pytest.raises(ComfyUIMalformedResponse):
        HttpComfyUIClient("http://test").submit_workflow({})


def test_history_completed_status(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"abc": {"status": {"completed": True, "status_str": "success"}, "outputs": {}}}
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: DummyResponse(payload))

    result = HttpComfyUIClient("http://test").get_history("abc")

    assert result.status == "completed"
