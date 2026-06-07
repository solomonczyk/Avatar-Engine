# 10. Git Workflow

## Repositories

Source reference:

```text
https://github.com/solomonczyk/comfy-agent-mvp
```

Target:

```text
git@github.com:solomonczyk/Avatar-Engine.git
```

All Avatar Engine development is committed only to the target repository.

## Branch

For a single developer MVP:

```text
main
```

Feature branches are optional, not mandatory.

## Commit rule

One completed feature/layer per commit group.

Examples:

```text
docs: add Avatar Engine development specification
feat: add persistent local job queue
feat: add single GPU worker
feat: integrate ComfyUI workflow execution
feat: add talking avatar stage
test: add local end-to-end avatar pipeline coverage
```

## Before commit

```powershell
pytest -q
git status --short
git diff --check
```

## Push

```powershell
git add .
git commit -m "..."
git push origin main
git status --short
```

Final `git status --short` must be empty.

## Do not commit

- `.env`;
- keys;
- model weights;
- generated videos;
- personal photos/audio;
- SQLite DB;
- logs;
- temporary files;
- reference clone of `comfy-agent-mvp`.

## Reuse traceability

Every copied/adapted source file must be mentioned in `docs/REUSE_LEDGER.md`.
