from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from avatar_engine.db import connect, init_database
from avatar_engine.jobs.state import JobState, StageState
from avatar_engine.models import Artifact, Job, JobStage


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        status=row["status"],
        current_stage=row["current_stage"],
        input_json=json.loads(row["input_json"]),
        output_json=json.loads(row["output_json"]),
        error_message=row["error_message"],
        retry_count=row["retry_count"],
    )


def _stage(row: sqlite3.Row) -> JobStage:
    return JobStage(
        id=row["id"],
        job_id=row["job_id"],
        stage_name=row["stage_name"],
        stage_order=row["stage_order"],
        status=row["status"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        duration_ms=row["duration_ms"],
        stdout_path=row["stdout_path"],
        stderr_path=row["stderr_path"],
        error_message=row["error_message"],
    )


class JobRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def init(self) -> None:
        init_database(self.db_path)

    def create_job(self, input_data: dict[str, Any], stage_names: list[str]) -> str:
        self.init()
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        now = utc_now()
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO jobs(id, created_at, updated_at, status, current_stage, input_json, output_json, retry_count)
                VALUES (?, ?, ?, ?, NULL, ?, '{}', 0)
                """,
                (job_id, now, now, JobState.QUEUED.value, json.dumps(input_data, sort_keys=True)),
            )
            for order, name in enumerate(stage_names, start=1):
                conn.execute(
                    """
                    INSERT INTO job_stages(job_id, stage_name, stage_order, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (job_id, name, order, StageState.PENDING.value),
                )
            self.add_event_conn(conn, job_id, "job_created", {"stage_count": len(stage_names)})
            conn.commit()
        return job_id

    def list_jobs(self) -> list[Job]:
        self.init()
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at ASC").fetchall()
        return [_job(row) for row in rows]

    def get_job(self, job_id: str) -> Job | None:
        self.init()
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _job(row) if row else None

    def get_stages(self, job_id: str) -> list[JobStage]:
        self.init()
        with connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM job_stages WHERE job_id = ? ORDER BY stage_order ASC",
                (job_id,),
            ).fetchall()
        return [_stage(row) for row in rows]

    def get_artifacts(self, job_id: str) -> list[sqlite3.Row]:
        self.init()
        with connect(self.db_path) as conn:
            return conn.execute(
                "SELECT * FROM artifacts WHERE job_id = ? ORDER BY id ASC",
                (job_id,),
            ).fetchall()

    def claim_next_job(self, mode: str | None = None) -> str | None:
        self.init()
        now = utc_now()
        with connect(self.db_path) as conn:
            conn.isolation_level = None
            conn.execute("BEGIN IMMEDIATE")
            running = conn.execute(
                "SELECT id FROM jobs WHERE status = ? LIMIT 1",
                (JobState.RUNNING.value,),
            ).fetchone()
            if running:
                conn.execute("COMMIT")
                return None
            if mode is None:
                row = conn.execute(
                    """
                    SELECT id FROM jobs
                    WHERE status = ?
                    ORDER BY created_at ASC
                    LIMIT 1
                    """,
                    (JobState.QUEUED.value,),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT id FROM jobs
                    WHERE status = ? AND json_extract(input_json, '$.mode') = ?
                    ORDER BY created_at ASC
                    LIMIT 1
                    """,
                    (JobState.QUEUED.value, mode),
                ).fetchone()
            if not row:
                conn.execute("COMMIT")
                return None
            job_id = row["id"]
            conn.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?",
                (JobState.RUNNING.value, now, job_id),
            )
            self.add_event_conn(conn, job_id, "job_claimed", {})
            conn.execute("COMMIT")
            return job_id

    def update_job(
        self,
        job_id: str,
        status: JobState,
        *,
        current_stage: str | None = None,
        output: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        now = utc_now()
        with connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = ?, current_stage = ?, output_json = COALESCE(?, output_json),
                    error_message = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status.value,
                    current_stage,
                    json.dumps(output, sort_keys=True) if output is not None else None,
                    error_message,
                    now,
                    job_id,
                ),
            )
            self.add_event_conn(conn, job_id, "job_status_changed", {"status": status.value})
            conn.commit()

    def update_stage(
        self,
        job_id: str,
        stage_name: str,
        status: StageState,
        *,
        started_at: str | None = None,
        finished_at: str | None = None,
        duration_ms: int | None = None,
        stdout_path: str | None = None,
        stderr_path: str | None = None,
        error_message: str | None = None,
    ) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE job_stages
                SET status = ?, started_at = COALESCE(?, started_at),
                    finished_at = COALESCE(?, finished_at),
                    duration_ms = COALESCE(?, duration_ms),
                    stdout_path = COALESCE(?, stdout_path),
                    stderr_path = COALESCE(?, stderr_path),
                    error_message = ?
                WHERE job_id = ? AND stage_name = ?
                """,
                (
                    status.value,
                    started_at,
                    finished_at,
                    duration_ms,
                    stdout_path,
                    stderr_path,
                    error_message,
                    job_id,
                    stage_name,
                ),
            )
            self.add_event_conn(conn, job_id, "stage_status_changed", {"stage": stage_name, "status": status.value})
            conn.commit()

    def skip_remaining_stages(self, job_id: str, after_stage_order: int) -> None:
        with connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT stage_name FROM job_stages
                WHERE job_id = ? AND stage_order > ? AND status = ?
                ORDER BY stage_order ASC
                """,
                (job_id, after_stage_order, StageState.PENDING.value),
            ).fetchall()
            for row in rows:
                conn.execute(
                    "UPDATE job_stages SET status = ? WHERE job_id = ? AND stage_name = ?",
                    (StageState.SKIPPED.value, job_id, row["stage_name"]),
                )
            self.add_event_conn(conn, job_id, "remaining_stages_skipped", {"count": len(rows)})
            conn.commit()

    def add_artifact(self, job_id: str, stage_name: str, artifact: Artifact) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO artifacts(job_id, stage_name, artifact_type, path, sha256, size_bytes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    stage_name,
                    artifact.artifact_type,
                    str(artifact.path),
                    artifact.sha256,
                    artifact.size_bytes,
                    utc_now(),
                ),
            )
            conn.commit()

    def add_event(self, job_id: str | None, event_type: str, payload: dict[str, Any]) -> None:
        with connect(self.db_path) as conn:
            self.add_event_conn(conn, job_id, event_type, payload)
            conn.commit()

    def add_event_conn(
        self,
        conn: sqlite3.Connection,
        job_id: str | None,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        conn.execute(
            "INSERT INTO events(job_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (job_id, event_type, json.dumps(payload, sort_keys=True), utc_now()),
        )
