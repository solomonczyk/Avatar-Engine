# 06. Local Setup

## Clone target repository

```powershell
cd F:\Dev\Projects
git clone git@github.com:solomonczyk/Avatar-Engine.git "Avatar Engine"
cd "Avatar Engine"
```

## Optional read-only source clone

```powershell
cd F:\Dev\Projects
git clone https://github.com/solomonczyk/comfy-agent-mvp.git comfy-agent-mvp-reference
```

Do not place the source clone inside Avatar Engine and do not push changes to it.

## Python

Use Python 3.11 for the core application. Heavy external runtimes may use separate virtual environments, for example `.venv-core`, `.venv-sadtalker` and `.venv-lipsync`.

## Core setup

```powershell
py -3.11 -m venv .venv-core
.\.venv-core\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Verification

```powershell
avatar-engine doctor
pytest -q
avatar-engine init-db
avatar-engine list-jobs
```
