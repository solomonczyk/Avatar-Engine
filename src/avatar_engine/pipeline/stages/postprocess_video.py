from __future__ import annotations

from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, text_artifact


class PostprocessVideoStage:
    name = "postprocess_video"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        artifact = text_artifact(
            context,
            self.name,
            "video_placeholder",
            "video_placeholder.txt",
            "Fake postprocess completed. No real MP4 was created.\n",
        )
        return StageResult(artifacts=[artifact], stdout="video placeholder postprocessed")
