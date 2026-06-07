# Avatar Engine

Avatar Engine is a local, single-user foundation for building an avatar generation pipeline on Windows. This layer keeps the original fake pipeline and adds one controlled real ComfyUI image-generation path.

This layer does not run talking avatar, video, lip-sync, TTS, face swap, upscale, automatic retry, or production acceptance.

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

## One Real ComfyUI Image

Requires local ComfyUI:

```dotenv
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_ROOT=F:\ComfyUI
```

Commands:

```powershell
avatar-engine comfyui-health
avatar-engine create-job `
  --mode comfyui-image `
  --workflow "workflows\simple_portrait.json" `
  --prompt "portrait of a fictional adult digital presenter, front-facing, neutral expression, simple studio background, soft lighting, realistic skin, clear eyes, high detail" `
  --negative-prompt "deformed face, extra eyes, extra mouth, duplicate face, bad anatomy, blurry, low quality, text, watermark" `
  --seed 20260607 `
  --width 512 `
  --height 512 `
  --steps 15 `
  --cfg 6.5
avatar-engine run-worker --once --mode comfyui-image
avatar-engine show-job <job_id>
```

The job writes `job.json`, preflight, source/patched workflow snapshots, patch report, submit/history logs, one output image, `image_validation.json`, `manifest.json`, and `operator_review_packet.json` under `data/jobs/<job_id>/`. A technically valid image stops at `operator_visual_review_required`.

## Project Shape

```text
CLI
-> SQLite job queue
-> single worker
-> sequential fake or comfyui_image pipeline
-> fake or real ComfyUI interface
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
- Real generation is limited to one `comfyui_image` submit per job.
- No production acceptance without manual operator review.

## Commands

```powershell
avatar-engine doctor
avatar-engine init-db
avatar-engine create-job --dry-run
avatar-engine list-jobs
avatar-engine show-job <job_id>
avatar-engine comfyui-health
avatar-engine run-worker --once --mode fake
avatar-engine run-worker --once --mode comfyui-image
avatar-engine review <job_id> --accept
avatar-engine review <job_id> --reject --notes "reason"
```

## Tests

```powershell
python -m compileall src
pytest -q
```

Runtime data is written under `data/` and ignored by Git except placeholder files that keep the directory structure visible.
