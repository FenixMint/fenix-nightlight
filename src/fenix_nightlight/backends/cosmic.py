from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .base import Backend, BackendError


class CosmicBackend(Backend):
    name = "cosmic"

    def __init__(self, helper_path: str):
        self.helper_path = helper_path

    def _resolved_helper(self) -> str | None:
        candidate = Path(self.helper_path).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        return shutil.which("cosmic-nightlight-helper")

    def available(self) -> bool:
        return self._resolved_helper() is not None

    def _run(self, *arguments: str) -> None:
        helper = self._resolved_helper()
        if not helper:
            raise BackendError("COSMIC backend unavailable: cosmic-nightlight-helper was not found or is not executable")
        result = subprocess.run([helper, *arguments], text=True, capture_output=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise BackendError(detail or f"helper exited with status {result.returncode}")

    def apply(self, temperature: int, brightness: float) -> None:
        self._run("--temp", str(int(temperature)), "--brightness", f"{brightness:.3f}")

    def off(self) -> None:
        self._run("--off")
