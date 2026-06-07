# 07. GPU Queue and Resource Policy

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
