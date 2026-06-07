from __future__ import annotations

import json

from avatar_engine.jobs.repository import JobRepository, utc_now
from avatar_engine.jobs.state import JobState


def review_job(repository: JobRepository, job_id: str, *, accept: bool, notes: str = "") -> str:
    job = repository.get_job(job_id)
    if job is None:
        raise ValueError(f"Unknown job: {job_id}")
    if job.status != JobState.OPERATOR_VISUAL_REVIEW_REQUIRED.value:
        raise ValueError("Job can only be reviewed from operator_visual_review_required")

    target = JobState.ACCEPTED if accept else JobState.REJECTED
    output = dict(job.output_json)
    output["operator_visual_review"] = "accepted" if accept else "rejected"
    output["production_accepted"] = bool(accept)
    output["reviewed_at"] = utc_now()
    output["review_notes"] = notes
    repository.update_job(job_id, target, output=output)

    manifest_path = output.get("manifest_path")
    if manifest_path:
        try:
            from pathlib import Path

            path = Path(manifest_path)
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["operator_visual_review"] = output["operator_visual_review"]
            manifest["production_accepted"] = bool(accept)
            path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        except OSError:
            pass
    return target.value
