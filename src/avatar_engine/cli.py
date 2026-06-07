from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Optional

import httpx
import typer

from avatar_engine.config import get_settings
from avatar_engine.db import init_database
from avatar_engine.integrations.comfyui.client import HttpComfyUIClient
from avatar_engine.pipeline.stages.comfyui_image import DEFAULT_NEGATIVE_PROMPT, DEFAULT_PROMPT
from avatar_engine.jobs.repository import JobRepository
from avatar_engine.jobs.service import JobService
from avatar_engine.jobs.worker import Worker
from avatar_engine.review.operator_review import review_job

app = typer.Typer(help="Local Avatar Engine CLI")


@app.command()
def doctor(check_comfyui: bool = False) -> None:
    settings = get_settings()
    settings.ensure_directories()
    init_database(settings.db_path)
    git_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=settings.project_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    comfyui_status = "not_checked"
    if check_comfyui:
        comfyui_status = HttpComfyUIClient(settings.comfyui_base_url).health().status
    payload = {
        "python_version": sys.version.split()[0],
        "project_root": str(settings.project_root),
        "data_dir": str(settings.data_dir),
        "db_path": str(settings.db_path),
        "db_available": settings.db_path.exists(),
        "git_root": git_root,
        "comfyui_base_url": settings.comfyui_base_url,
        "comfyui": comfyui_status,
        "ffmpeg_available": shutil.which(settings.ffmpeg_path) is not None,
        "gpu_worker_concurrency": settings.gpu_worker_concurrency,
        "auto_retry": settings.auto_retry,
        "pass": settings.gpu_worker_concurrency == 1 and settings.auto_retry is False,
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("comfyui-health")
def comfyui_health() -> None:
    settings = get_settings()
    client = HttpComfyUIClient(settings.comfyui_base_url)
    health = client.health()
    payload = {
        "comfyui_reachable": health.available,
        "base_url": settings.comfyui_base_url,
        "system_stats_received": False,
        "object_info_received": False,
        "history_received": False,
    }
    if health.available:
        payload["system_stats_received"] = client.get_system_stats().received
        payload["object_info_received"] = client.get_object_info().received
        try:
            response = httpx.get(f"{settings.comfyui_base_url.rstrip('/')}/history", timeout=10.0)
            payload["history_received"] = response.is_success
            payload["history_status_code"] = response.status_code
        except httpx.HTTPError as exc:
            payload["history_error"] = str(exc)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("init-db")
def init_db() -> None:
    settings = get_settings()
    settings.ensure_directories()
    init_database(settings.db_path)
    typer.echo(f"Initialized {settings.db_path}")


@app.command("create-job")
def create_job(
    portrait: Optional[str] = typer.Option(None, "--portrait"),
    audio: Optional[str] = typer.Option(None, "--audio"),
    reference_image: Optional[str] = typer.Option(None, "--reference-image"),
    text: Optional[str] = typer.Option(None, "--text"),
    mode: str = typer.Option("fake", "--mode"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    workflow: str = typer.Option("workflows/simple_portrait.json", "--workflow"),
    prompt: str = typer.Option(DEFAULT_PROMPT, "--prompt"),
    negative_prompt: str = typer.Option(DEFAULT_NEGATIVE_PROMPT, "--negative-prompt"),
    checkpoint: Optional[str] = typer.Option(None, "--checkpoint"),
    seed: int = typer.Option(20260607, "--seed"),
    width: int = typer.Option(512, "--width"),
    height: int = typer.Option(512, "--height"),
    steps: int = typer.Option(15, "--steps"),
    cfg: float = typer.Option(6.5, "--cfg"),
    sampler: str = typer.Option("euler", "--sampler"),
    scheduler: str = typer.Option("normal", "--scheduler"),
) -> None:
    normalized_mode = mode.replace("-", "_")
    if normalized_mode == "fake":
        job_id = JobService().create_fake_job(portrait=portrait, audio=audio, dry_run=dry_run, mode="fake")
    elif normalized_mode == "comfyui_image":
        job_id = JobService().create_comfyui_image_job(
            workflow=workflow,
            prompt=prompt,
            negative_prompt=negative_prompt,
            checkpoint=checkpoint,
            seed=seed,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            sampler=sampler,
            scheduler=scheduler,
        )
    elif normalized_mode == "talking_head":
        if reference_image is None:
            raise typer.BadParameter("--reference-image is required for talking-head mode")
        job_id = JobService().create_talking_head_job(
            reference_image=reference_image,
            audio=audio,
            text=text,
        )
    else:
        raise typer.BadParameter("Mode must be fake, comfyui-image, or talking-head")
    typer.echo(job_id)


@app.command("list-jobs")
def list_jobs() -> None:
    settings = get_settings()
    repo = JobRepository(settings.db_path)
    rows = [
        {
            "id": job.id,
            "status": job.status,
            "current_stage": job.current_stage,
            "retry_count": job.retry_count,
            "created_at": job.created_at,
        }
        for job in repo.list_jobs()
    ]
    typer.echo(json.dumps(rows, indent=2, sort_keys=True))


@app.command("show-job")
def show_job(job_id: str) -> None:
    settings = get_settings()
    repo = JobRepository(settings.db_path)
    job = repo.get_job(job_id)
    if job is None:
        raise typer.BadParameter(f"Unknown job: {job_id}")
    payload = {
        "job": job.__dict__,
        "stages": [stage.__dict__ for stage in repo.get_stages(job_id)],
        "artifacts": [dict(row) for row in repo.get_artifacts(job_id)],
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))


@app.command("run-worker")
def run_worker(once: bool = typer.Option(False, "--once"), mode: str = typer.Option("auto", "--mode")) -> None:
    if not once:
        raise typer.BadParameter("Bootstrap worker requires --once")
    job_id = Worker().run_once(mode=mode)
    typer.echo(job_id or "no queued job")


@app.command()
def review(
    job_id: str,
    accept: bool = typer.Option(False, "--accept"),
    reject: bool = typer.Option(False, "--reject"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    if accept == reject:
        raise typer.BadParameter("Choose exactly one of --accept or --reject")
    settings = get_settings()
    repo = JobRepository(settings.db_path)
    status = review_job(repo, job_id, accept=accept, notes=notes)
    typer.echo(status)
