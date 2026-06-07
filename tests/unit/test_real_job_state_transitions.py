from pathlib import Path

from PIL import Image

from avatar_engine.config import Settings
from avatar_engine.integrations.comfyui.fake_client import FakeComfyUIClient
from avatar_engine.jobs.repository import JobRepository
from avatar_engine.jobs.state import JobState
from avatar_engine.models import ComfyUIOutput, SubmitResult
from avatar_engine.pipeline.runner import PipelineRunner
from avatar_engine.pipeline.stages.comfyui_image import comfyui_image_stages


class DownloadingFakeComfyUIClient(FakeComfyUIClient):
    def submit_workflow(self, workflow: dict) -> SubmitResult:
        return SubmitResult(prompt_id=self.prompt_id, submitted=True, details={"fake": True})

    def collect_outputs(self, prompt_id: str) -> list[ComfyUIOutput]:
        return [ComfyUIOutput(prompt_id=prompt_id, node_id="9", filename="generated.png", subfolder="", output_type="output")]

    def download_output(self, output: ComfyUIOutput, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (512, 512))
        image.putdata([(x % 255, y % 255, (x + y) % 255) for y in range(512) for x in range(512)])
        image.save(destination)


def test_comfyui_image_job_stops_at_operator_review(settings: Settings) -> None:
    settings.comfyui_root = settings.project_root / "comfyui"
    repo = JobRepository(settings.db_path)
    workflow = settings.project_root / "workflow.json"
    workflow.write_text(
        """
        {
          "3": {"inputs": {"seed": 1, "steps": 1, "cfg": 1, "sampler_name": "euler", "scheduler": "normal", "denoise": 1}, "class_type": "KSampler"},
          "4": {"inputs": {"ckpt_name": "fake.safetensors"}, "class_type": "CheckpointLoaderSimple"},
          "5": {"inputs": {"width": 512, "height": 512, "batch_size": 1}, "class_type": "EmptyLatentImage"},
          "6": {"inputs": {"text": "p"}, "class_type": "CLIPTextEncode"},
          "7": {"inputs": {"text": "n"}, "class_type": "CLIPTextEncode"},
          "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
          "9": {"inputs": {"filename_prefix": "x", "images": ["8", 0]}, "class_type": "SaveImage"}
        }
        """,
        encoding="utf-8",
    )
    (settings.comfyui_root / "models" / "checkpoints").mkdir(parents=True)
    (settings.comfyui_root / "models" / "checkpoints" / "fake.safetensors").write_text("fake", encoding="utf-8")
    repo.init()
    job_id = repo.create_job(
        {
            "mode": "comfyui_image",
            "workflow": str(workflow),
            "checkpoint": "fake.safetensors",
            "width": 512,
            "height": 512,
            "steps": 1,
            "cfg": 1,
            "automatic_retry": False,
        },
        [stage.name for stage in comfyui_image_stages()],
    )

    PipelineRunner(settings, repo, comfyui_image_stages(DownloadingFakeComfyUIClient())).run(job_id)

    job = repo.get_job(job_id)
    assert job is not None
    assert job.status == JobState.OPERATOR_VISUAL_REVIEW_REQUIRED.value
    assert job.output_json["production_accepted"] is False
