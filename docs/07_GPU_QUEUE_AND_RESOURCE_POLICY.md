# 07. GPU Queue and Resource Policy

## Purpose

Stable sequential execution is more important than parallel speed on GTX 1060 5 GB.

## Mandatory settings

- GPU worker concurrency: 1
- parallel GPU stages: disabled
- automatic retry: disabled
- blind retry: disabled

## Lock

Use a simple process lock at `data/runtime/gpu.lock`. It stores PID, job ID, stage and start time. A worker must verify the lock before every GPU stage and reject a second active worker.

## GPU stages

Image generation, CUDA face processing, talking-avatar inference, lip-sync and AI upscale are always sequential.

## Failure handling

On CUDA out-of-memory or runtime failure:

1. mark the stage failed;
2. mark the job failed;
3. save stdout and stderr;
4. release the lock;
5. do not retry automatically;
6. let the operator change resolution or runtime.

## Model lifecycle

Prefer isolated subprocess runtimes. Ending a process releases VRAM more reliably than keeping several large Python models in one long-lived process.

A configurable pause between heavy stages is allowed. Complex temperature automation is not required for MVP.
