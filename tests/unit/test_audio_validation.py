from avatar_engine.integrations.talking_head.audio import validate_audio


def test_audio_validation_accepts_short_wav(sample_audio) -> None:
    result = validate_audio(sample_audio)

    assert result["file_exists"] is True
    assert result["audio_stream_present"] is True
    assert result["duration_in_allowed_range"] is True
    assert result["sha256"]
    assert result["audio_valid"] is True
