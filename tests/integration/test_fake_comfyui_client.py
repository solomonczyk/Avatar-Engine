from avatar_engine.integrations.comfyui.fake_client import FakeComfyUIClient


def test_fake_comfyui_client_never_submits_real_workflow() -> None:
    client = FakeComfyUIClient()
    submit = client.submit_workflow({"nodes": {}})
    assert submit.prompt_id == "fake-prompt-avatar-engine-0001"
    assert submit.submitted is False
    assert client.health().available is True
    assert client.collect_outputs(submit.prompt_id)[0].filename == "fake.png"
