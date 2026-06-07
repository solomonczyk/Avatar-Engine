# 04. Project Structure

```text
Avatar Engine/
├─ src/avatar_engine/
│  ├─ cli.py
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  ├─ jobs/
│  ├─ pipeline/stages/
│  ├─ integrations/comfyui/
│  ├─ integrations/tts/
│  ├─ integrations/talking_avatar/
│  ├─ integrations/ffmpeg/
│  ├─ resources/
│  └─ review/
├─ workflows/
├─ config/
├─ data/
├─ models/
├─ scripts/
├─ tests/unit/
├─ tests/integration/
├─ tests/e2e/
├─ docs/
├─ .env.example
├─ .gitignore
├─ pyproject.toml
├─ README.md
└─ AGENTS.md
```

## Tracked

Source code, tests, small workflow JSON files, documentation, configuration examples and small fixtures.

## Not tracked

Secrets, model weights, input portraits and audio, generated media, SQLite runtime database, logs, temporary files, ComfyUI installation and virtual environments.
