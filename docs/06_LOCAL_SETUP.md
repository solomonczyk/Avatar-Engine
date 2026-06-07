# 06. Local Setup

## Controlled ComfyUI image execution

Start local ComfyUI separately and verify:

```powershell
avatar-engine comfyui-health
```

Queue and run one real image job:

```powershell
avatar-engine create-job `
  --mode comfyui-image `
  --workflow "workflows\simple_portrait.json" `
  --seed 20260607 `
  --width 512 `
  --height 512 `
  --steps 15 `
  --cfg 6.5

avatar-engine run-worker --once --mode comfyui-image
avatar-engine show-job <job_id>
```

Do not rerun the worker for the same job after a submit. A valid image stops at `operator_visual_review_required`; use `review` only after manual visual inspection.

## Talking-head input validation

Universal audio-file command:

```powershell
avatar-engine create-job `
  --mode talking-head `
  --reference-image "<path>" `
  --audio "<path>"

avatar-engine run-worker --once --mode talking-head
```

Universal text command:

```powershell
avatar-engine create-job `
  --mode talking-head `
  --reference-image "<path>" `
  --text "<text>"

avatar-engine run-worker --once --mode talking-head
```

The reference image is job input, not a global default. If no local talking-head runtime is fully ready and authorized, the worker writes a runtime-selection artifact and stops before execution. Normal tests use only the explicit fake runtime.

## Target

```powershell
cd F:\Dev\Projects
git clone git@github.com:solomonczyk/Avatar-Engine.git "Avatar Engine"
cd "Avatar Engine"
```

## Optional source reference

Clone the source project beside the new project, not inside it:

```powershell
cd F:\Dev\Projects
git clone https://github.com/solomonczyk/comfy-agent-mvp.git comfy-agent-mvp-reference
```

Do not change or push from the reference clone.

## Python

Recommended:

```text
Python 3.11
```

Some avatar repositories have older or conflicting dependencies. Avoid forcing every model into one environment.

Suggested environments:

```text
.venv-core
.venv-sadtalker
.venv-lipsync
```

The core application launches external runtimes as subprocesses.

## Core setup

```powershell
py -3.11 -m venv .venv-core
.\.venv-core\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Environment

Copy:

```powershell
Copy-Item .env.example .env
```

Example variables:

```dotenv
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_ROOT=F:\ComfyUI
AVATAR_ENGINE_DATA_DIR=F:\Dev\Projects\Avatar Engine\data
AVATAR_ENGINE_DB_PATH=F:\Dev\Projects\Avatar Engine\data\avatar_engine.db
GPU_WORKER_CONCURRENCY=1
AUTO_RETRY=false
FFMPEG_PATH=ffmpeg
```

## Verification

```powershell
avatar-engine doctor
pytest -q
avatar-engine init-db
avatar-engine list-jobs
```

## Bootstrap fake execution

```powershell
avatar-engine init-db
avatar-engine create-job --dry-run
avatar-engine run-worker --once --mode fake
avatar-engine list-jobs
```

The fake worker writes a job folder under `data/jobs/<job_id>/` and creates `manifest.json`. It does not submit a ComfyUI workflow, run GPU commands, create real video, perform automatic retry, or mark production acceptance.
