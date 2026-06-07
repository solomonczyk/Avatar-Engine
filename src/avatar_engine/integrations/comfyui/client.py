from __future__ import annotations

from pathlib import Path
from time import monotonic, sleep
from typing import Any

import httpx

from avatar_engine.models import ComfyUIOutput, HealthResult, HistoryResult, ObjectInfoResult, SubmitResult, SystemStatsResult


class ComfyUIClientError(RuntimeError):
    pass


class ComfyUIHTTPError(ComfyUIClientError):
    pass


class ComfyUIMalformedResponse(ComfyUIClientError):
    pass


class ComfyUITimeout(ComfyUIClientError):
    pass


class HttpComfyUIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, path: str) -> dict[str, Any]:
        try:
            response = httpx.get(f"{self.base_url}{path}", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ComfyUIHTTPError(f"ComfyUI GET {path} returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ComfyUIHTTPError(f"ComfyUI GET {path} failed: {exc}") from exc
        except ValueError as exc:
            raise ComfyUIMalformedResponse(f"ComfyUI GET {path} returned non-JSON") from exc
        if not isinstance(data, dict):
            raise ComfyUIMalformedResponse(f"ComfyUI GET {path} returned {type(data).__name__}, expected object")
        return data

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise ComfyUIHTTPError(f"ComfyUI POST {path} returned HTTP {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise ComfyUIHTTPError(f"ComfyUI POST {path} failed: {exc}") from exc
        except ValueError as exc:
            raise ComfyUIMalformedResponse(f"ComfyUI POST {path} returned non-JSON") from exc
        if not isinstance(data, dict):
            raise ComfyUIMalformedResponse(f"ComfyUI POST {path} returned {type(data).__name__}, expected object")
        return data

    def health(self) -> HealthResult:
        try:
            response = httpx.get(f"{self.base_url}/system_stats", timeout=self.timeout)
            return HealthResult(
                available=response.is_success,
                status="available" if response.is_success else "unavailable",
                details={"status_code": response.status_code},
            )
        except httpx.HTTPError as exc:
            return HealthResult(available=False, status="unavailable", details={"error": str(exc)})

    def get_system_stats(self) -> SystemStatsResult:
        return SystemStatsResult(received=True, details=self._get_json("/system_stats"))

    def get_object_info(self) -> ObjectInfoResult:
        return ObjectInfoResult(received=True, details=self._get_json("/object_info"))

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        data = self._post_json("/prompt", {"prompt": workflow})
        prompt_id = data.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id.strip():
            raise ComfyUIMalformedResponse("ComfyUI submit response did not include a valid prompt_id")
        return SubmitResult(prompt_id=prompt_id, submitted=True, details=data)

    def get_history(self, prompt_id: str) -> HistoryResult:
        if not prompt_id.strip():
            raise ValueError("prompt_id must be non-empty")
        data = self._get_json(f"/history/{prompt_id}")
        entry = data.get(prompt_id)
        if entry is None:
            return HistoryResult(prompt_id=prompt_id, status="pending", details=data)
        if not isinstance(entry, dict):
            raise ComfyUIMalformedResponse("ComfyUI history entry is not an object")
        status = entry.get("status", {})
        if not isinstance(status, dict):
            raise ComfyUIMalformedResponse("ComfyUI history status is not an object")
        status_str = str(status.get("status_str", "")).lower()
        completed = bool(status.get("completed", False))
        if completed and status_str in {"success", "completed"}:
            return HistoryResult(prompt_id=prompt_id, status="completed", details=entry)
        if "error" in status_str or "failed" in status_str:
            return HistoryResult(prompt_id=prompt_id, status="failed", details=entry)
        return HistoryResult(prompt_id=prompt_id, status="running", details=entry)

    def wait_for_completion(self, prompt_id: str, timeout_seconds: float, poll_interval: float) -> HistoryResult:
        deadline = monotonic() + timeout_seconds
        while monotonic() < deadline:
            history = self.get_history(prompt_id)
            if history.status in {"completed", "failed"}:
                return history
            sleep(poll_interval)
        raise ComfyUITimeout(f"Timed out waiting for ComfyUI prompt {prompt_id}")

    def collect_outputs(self, prompt_id: str) -> list[ComfyUIOutput]:
        history = self.get_history(prompt_id)
        if history.status != "completed":
            raise ComfyUIClientError(f"Cannot collect outputs for prompt {prompt_id} with status {history.status}")
        outputs = history.details.get("outputs", {})
        if not isinstance(outputs, dict):
            raise ComfyUIMalformedResponse("ComfyUI outputs field is not an object")
        collected: list[ComfyUIOutput] = []
        for node_id, node_outputs in outputs.items():
            if not isinstance(node_outputs, dict):
                continue
            images = node_outputs.get("images", [])
            if not isinstance(images, list):
                continue
            for image in images:
                if not isinstance(image, dict):
                    continue
                filename = image.get("filename")
                if not isinstance(filename, str) or not filename:
                    continue
                collected.append(
                    ComfyUIOutput(
                        prompt_id=prompt_id,
                        node_id=str(node_id),
                        filename=filename,
                        subfolder=str(image.get("subfolder", "")),
                        output_type=str(image.get("type", "output")),
                    )
                )
        return collected

    def download_output(self, output: ComfyUIOutput, destination: Path) -> None:
        params = {
            "filename": output.filename,
            "subfolder": output.subfolder,
            "type": output.output_type,
        }
        try:
            response = httpx.get(f"{self.base_url}/view", params=params, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ComfyUIHTTPError(f"ComfyUI output download returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ComfyUIHTTPError(f"ComfyUI output download failed: {exc}") from exc
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
