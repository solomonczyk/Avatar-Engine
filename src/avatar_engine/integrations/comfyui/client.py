from __future__ import annotations

import httpx

from avatar_engine.models import Artifact, HealthResult, HistoryResult, SubmitResult


class HttpComfyUIClient:
    def __init__(self, base_url: str, timeout: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

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

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        raise NotImplementedError("Real ComfyUI workflow submission is not enabled in the bootstrap layer")

    def get_history(self, prompt_id: str) -> HistoryResult:
        raise NotImplementedError("Real ComfyUI history polling is not enabled in the bootstrap layer")

    def collect_outputs(self, prompt_id: str) -> list[Artifact]:
        raise NotImplementedError("Real ComfyUI output collection is not enabled in the bootstrap layer")
