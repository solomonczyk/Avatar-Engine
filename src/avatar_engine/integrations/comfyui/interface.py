from __future__ import annotations

from typing import Protocol

from avatar_engine.models import Artifact, HealthResult, HistoryResult, SubmitResult


class ComfyUIClient(Protocol):
    def health(self) -> HealthResult:
        ...

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        ...

    def get_history(self, prompt_id: str) -> HistoryResult:
        ...

    def collect_outputs(self, prompt_id: str) -> list[Artifact]:
        ...
