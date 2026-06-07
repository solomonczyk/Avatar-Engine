from __future__ import annotations

from avatar_engine.models import ComfyUIOutput, HealthResult, HistoryResult, ObjectInfoResult, SubmitResult, SystemStatsResult


class FakeComfyUIClient:
    prompt_id = "fake-prompt-avatar-engine-0001"

    def health(self) -> HealthResult:
        return HealthResult(available=True, status="available", details={"fake": True})

    def get_system_stats(self) -> SystemStatsResult:
        return SystemStatsResult(received=True, details={"fake": True})

    def get_object_info(self) -> ObjectInfoResult:
        return ObjectInfoResult(
            received=True,
            details={
                "CheckpointLoaderSimple": {"input": {"required": {"ckpt_name": [["fake.safetensors"], {}]}}},
                "CLIPTextEncode": {},
                "KSampler": {},
                "EmptyLatentImage": {},
                "VAEDecode": {},
                "SaveImage": {},
            },
        )

    def submit_workflow(self, workflow: dict) -> SubmitResult:
        return SubmitResult(
            prompt_id=self.prompt_id,
            submitted=False,
            details={"fake": True, "workflow_keys": sorted(workflow.keys())},
        )

    def get_history(self, prompt_id: str) -> HistoryResult:
        return HistoryResult(prompt_id=prompt_id, status="completed", details={"fake": True})

    def wait_for_completion(self, prompt_id: str, timeout_seconds: float, poll_interval: float) -> HistoryResult:
        return self.get_history(prompt_id)

    def collect_outputs(self, prompt_id: str) -> list[ComfyUIOutput]:
        return [
            ComfyUIOutput(
                prompt_id=prompt_id,
                node_id="9",
                filename="fake.png",
                subfolder="",
                output_type="output",
            )
        ]
