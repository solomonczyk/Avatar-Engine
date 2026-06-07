from __future__ import annotations

from avatar_engine.pipeline.context import PipelineContext
from avatar_engine.pipeline.stages.base import StageResult, text_artifact


class PrepareAudioStage:
    name = "prepare_audio"
    uses_gpu = False

    def run(self, context: PipelineContext) -> StageResult:
        artifact = text_artifact(
            context,
            self.name,
            "audio_placeholder",
            "audio_placeholder.txt",
            "Fake audio prepared. No TTS or audio generation executed.\n",
        )
        return StageResult(artifacts=[artifact], stdout="audio placeholder prepared")
