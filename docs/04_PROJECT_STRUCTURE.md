# 04. Project Structure

## Real ComfyUI image additions

- `workflows/simple_portrait.json`: minimal one-image txt2img workflow.
- `src/avatar_engine/integrations/comfyui/client.py`: real HTTP health, submit, history, wait, and output download.
- `src/avatar_engine/integrations/comfyui/preflight.py`: workflow/model/node preflight.
- `src/avatar_engine/integrations/comfyui/generation_limit.py`: one-submit runtime counters.
- `src/avatar_engine/integrations/comfyui/image_validation.py`: Pillow technical validation.
- `src/avatar_engine/pipeline/stages/comfyui_image.py`: controlled real image pipeline.
- `src/avatar_engine/integrations/talking_head/`: reference/audio/video validation, runtime selection, fake subprocess adapter, and one-attempt counters.
- `src/avatar_engine/pipeline/stages/talking_head.py`: parameterized talking-head pipeline and blocker path.

```text
Avatar Engine/
├─ src/
│  └─ avatar_engine/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ models.py
│     ├─ db.py
│     ├─ jobs/
│     │  ├─ service.py
│     │  ├─ repository.py
│     │  ├─ state.py
│     │  └─ worker.py
│     ├─ pipeline/
│     │  ├─ runner.py
│     │  ├─ context.py
│     │  └─ stages/
│     │     ├─ validate_inputs.py
│     │     ├─ prepare_portrait.py
│     │     ├─ prepare_audio.py
│     │     ├─ animate_avatar.py
│     │     ├─ postprocess_video.py
│     │     └─ build_manifest.py
│     ├─ integrations/
│     │  ├─ comfyui/
│     │  │  ├─ client.py
│     │  │  ├─ workflow_loader.py
│     │  │  └─ workflow_patcher.py
│     │  ├─ tts/
│     │  ├─ talking_avatar/
│     │  └─ ffmpeg/
│     ├─ resources/
│     │  ├─ gpu_lock.py
│     │  └─ process_runner.py
│     └─ review/
│        └─ operator_review.py
├─ workflows/
├─ config/
├─ data/
│  ├─ input/
│  ├─ jobs/
│  ├─ output/
│  ├─ logs/
│  └─ avatar_engine.db
├─ models/
├─ scripts/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ e2e/
├─ docs/
├─ .env.example
├─ .gitignore
├─ pyproject.toml
├─ README.md
└─ AGENTS.md
```

## Git-tracked

- source code;
- tests;
- small workflow JSON files;
- docs;
- config examples;
- small fixtures;
- schema migrations if introduced.

## Not tracked

- `.env`;
- model weights;
- input photos/audio;
- generated images;
- generated videos;
- SQLite runtime database;
- logs;
- temp files;
- ComfyUI installation;
- virtual environments.

## Bootstrap implementation status

The standalone bootstrap now includes the required `src/avatar_engine` package, CLI, SQLite repository, fake pipeline stages, ComfyUI abstraction, tests, and runtime placeholder directories.

Runtime outputs under `data/jobs`, `data/logs`, `data/output`, `data/input`, `data/runtime`, and `data/avatar_engine.db` are ignored by Git. `.gitkeep` files keep the empty runtime folders visible.
