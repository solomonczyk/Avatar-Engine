# 04. Project Structure

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
