# 07. GPU Queue and Resource Policy

## ComfyUI image generation lock scope

For `comfyui_image`, the GPU stage is `submit_comfyui_workflow`. The lock covers the HTTP submit, ComfyUI history wait, output collection, and output download.

For `talking_head`, the GPU stage is `execute_talking_head_once`. The lock wraps one subprocess execution only. The lock payload includes `pid`, `job_id`, `stage`, `runtime`, and `started_at`; release is performed in the runner `finally` block.

The job records:

```json
{
  "submit_attempts": 1,
  "successful_submits": 1,
  "generation_attempts": 1,
  "max_generations": 1,
  "automatic_retry_executed": false
}
```

Any second submit attempt is blocked in-process. Polling `/history/<prompt_id>` is allowed and is not a second generation.

## Purpose

Не ускорять параллельностью, а обеспечить стабильное последовательное выполнение.

## Core rules

```json
{
  "gpu_worker_concurrency": 1,
  "automatic_retry": false,
  "blind_retry": false,
  "parallel_gpu_stages": false
}
```

Talking-head counters:

```json
{
  "talking_head_attempts": 0,
  "max_talking_head_generations": 1,
  "automatic_retry_enabled": false,
  "automatic_retry_executed": false,
  "second_runtime_attempted": false
}
```

After a talking-head subprocess starts, `talking_head_attempts` becomes `1`. Runtime switching after that point is a blocked second attempt.

## Lock

Использовать простой межпроцессный lock-файл:

```text
data/runtime/gpu.lock
```

Lock содержит:

```json
{
  "pid": 1234,
  "job_id": "job-...",
  "stage": "animate_avatar",
  "started_at": "..."
}
```

При старте worker проверяет:

- жив ли PID;
- не остался ли stale lock;
- не запущен ли уже другой worker.

## Stage categories

### CPU stages

- validate inputs;
- read/write SQLite;
- build manifest;
- hash files;
- FFmpeg audio inspection;
- copy artifacts.

### GPU stages

- image generation;
- face/identity embedding when CUDA используется;
- talking-avatar inference;
- lip-sync;
- AI upscale.

GPU stages всегда последовательны.

## Failure handling

При CUDA OOM:

1. stage получает `failed`;
2. job получает `failed`;
3. lock освобождается;
4. stderr сохраняется;
5. никакого автоматического повторения;
6. оператор решает, уменьшить ли resolution или сменить runtime.

## Temperature

Не нужна сложная автоматическая система. Достаточно:

- наблюдать температуру через NVIDIA tools;
- не запускать второй GPU stage;
- разрешить настраиваемую паузу между тяжёлыми стадиями;
- остановить worker вручную при нестабильности.

## Model lifecycle

Предпочтительно запускать тяжёлые runtimes отдельными subprocess-командами. После завершения процесса VRAM освобождается надёжнее, чем при загрузке нескольких моделей в один долгоживущий Python process.
