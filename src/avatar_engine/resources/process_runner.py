from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_process(command: list[str], timeout: int | None = None) -> ProcessResult:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    return ProcessResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
