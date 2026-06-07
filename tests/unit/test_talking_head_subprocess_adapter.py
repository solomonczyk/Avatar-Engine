from avatar_engine.integrations.talking_head.runtime import FakeTalkingHeadRuntime, TalkingHeadSettings


def test_fake_talking_head_adapter_writes_output(tmp_path, sample_reference_image, sample_audio) -> None:
    runtime = FakeTalkingHeadRuntime()
    result = runtime.generate(sample_reference_image, sample_audio, tmp_path, TalkingHeadSettings(timeout_seconds=60))

    assert result.returncode == 0
    assert result.output_video.exists()
    assert result.command[0] == "ffmpeg"
