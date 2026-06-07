# AGENTS.md

Avatar Engine is a local, single-user, non-commercial application.

## Keep it simple

Do not add multi-user support, authentication, cloud deployment, Kubernetes, Redis, Celery, PostgreSQL, distributed workers, a multi-agent runtime, automatic retry or an enterprise security framework.

## Runtime rules

- one GPU-heavy stage at a time;
- one local worker;
- SQLite persistence;
- no blind retry;
- technical success is not visual acceptance;
- manual operator review is required before accepted output.

## Source reuse

Treat `solomonczyk/comfy-agent-mvp` as read-only. Copy only required modules and record each adapted source file in `docs/REUSE_LEDGER.md`.

## Done means

Implementation, tests, artifacts, documentation update, proof file, commit, push and clean Git.
