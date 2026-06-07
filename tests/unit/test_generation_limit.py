import pytest

from avatar_engine.integrations.comfyui.generation_limit import GenerationCounters, GenerationLimitError


def test_second_submit_is_blocked() -> None:
    counters = GenerationCounters()
    counters.before_submit()
    counters.mark_submit_attempt()

    with pytest.raises(GenerationLimitError):
        counters.before_submit()

    assert counters.to_dict()["generation_attempts"] == 1
