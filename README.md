# Avatar Engine

Avatar Engine is a local, single-user foundation for building an avatar generation pipeline on Windows. This bootstrap layer is deliberately safe: it creates a Python package, SQLite job queue, one worker, fake pipeline stages, a fake ComfyUI client, CLI commands, tests, and proof artifacts.

This layer does not run real image, video, lip-sync, or ComfyUI generation.

## Quick Start

```powershell
py -3.11 -m venv .venv-core
.\.venv-core\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"

avatar-engine doctor
avatar-engine init-db
avatar-engine create-job --dry-run
avatar-engine run-worker --once --mode fake
avatar-engine list-jobs
```

## Project Shape

```text
CLI
-> SQLite job queue
-> single worker
-> sequential fake pipeline
-> fake ComfyUI interface
-> artifacts and manifests
-> operator visual review required
```

## Safety Boundaries

- Local Windows runtime only.
- One operator and one worker.
- SQLite only; no Redis, Celery, PostgreSQL, Kubernetes, or cloud deployment.
- No authentication, accounts, roles, public API, or multi-agent runtime.
- No heavy ML dependencies in the core package.
- No automatic retry.
- No real generation in this bootstrap layer.
- No production acceptance without manual operator review.

## Commands

```powershell
avatar-engine doctor
avatar-engine init-db
avatar-engine create-job --dry-run
avatar-engine list-jobs
avatar-engine show-job <job_id>
avatar-engine run-worker --once --mode fake
avatar-engine review <job_id> --accept
avatar-engine review <job_id> --reject --notes "reason"
```

## Tests

```powershell
python -m compileall src
pytest -q
```

Runtime data is written under `data/` and ignored by Git except placeholder files that keep the directory structure visible.
