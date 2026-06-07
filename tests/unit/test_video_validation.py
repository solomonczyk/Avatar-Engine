from avatar_engine.integrations.talking_head.runtime import FakeTalkingHeadRuntime, TalkingHeadSettings
from avatar_engine.integrations.talking_head.video_validation import validate_video


def test_video_validation_accepts_fake_runtime_mp4(tmp_path, sample_reference_image, sample_audio) -> None:
    result = FakeTalkingHeadRuntime().generate(sample_reference_image, sample_audio, tmp_path, TalkingHeadSettings(timeout_seconds=60))
    validation = validate_video(result.output_video, expected_audio_duration=3.2)

    assert validation["file_valid"] is True
    assert validation["video_stream_present"] is True
    assert validation["audio_stream_present"] is True
    assert validation["technical_validation"] == "passed"
