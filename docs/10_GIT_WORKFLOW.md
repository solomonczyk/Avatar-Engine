# 10. Git Workflow

## Repositories

Read-only source: `https://github.com/solomonczyk/comfy-agent-mvp`

Target: `git@github.com:solomonczyk/Avatar-Engine.git`

All development is committed only to the target repository.

## Branching

For this single-developer private MVP, direct work on `main` is allowed. Feature branches are optional.

## Commit examples

- `docs: add Avatar Engine development specification`
- `feat: add persistent local job queue`
- `feat: add single GPU worker`
- `feat: integrate ComfyUI workflow execution`
- `feat: add talking avatar stage`
- `test: add local end-to-end pipeline coverage`

## Before commit

```powershell
pytest -q
git diff --check
git status --short
```

## Finish

```powershell
git add .
git commit -m "..."
git push origin main
git status --short
```

The final status must be clean.

Never commit secrets, `.env`, model weights, generated media, personal inputs, the runtime database, logs or the read-only source clone.
