from __future__ import annotations

from typing import Protocol

from avatar_engine.models import ComfyUIOutput, HealthResult, HistoryResult, ObjectInfoResult, SubmitResult, SystemStatsResult


class ComfyUIClient(Protocol):
    def health(self) -> HealthResult:
        ...

    def get_system_stats(self) -> SystemStatsResult:
        ...

    def get_object_info(self) -> ObjectInfoResult:
        ...

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        ...

    def get_history(self, prompt_id: str) -> HistoryResult:
        ...

    def collect_outputs(self, prompt_id: str) -> list[ComfyUIOutput]:
        ...
