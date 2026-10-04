from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .base import Backend, BackendCapabilities, BackendError


class CosmicBackend(Backend):
    """Current COSMIC fallback using the external DRM/KMS helper.

    COSMIC does not yet expose a native night-light control path usable by this
    project. The helper therefore needs elevated privileges and may briefly
    flicker the display while it acquires DRM master.
    """

    name = "cosmic-drm"
    aliases = ("cosmic",)
    capabilities = BackendCapabilities(
        smooth_transitions=False,
        requires_privilege=True,
        may_flicker=True,
    )

    def __init__(self, helper_path: str, privileged_launcher: str = "pkexec"):
        self.helper_path = helper_path
        self.privileged_launcher = privileged_launcher

    def _resolved_helper(self) -> str | None:
        candidate = Path(self.helper_path).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        return shutil.which("cosmic-nightlight-helper")

    def _resolved_launcher(self) -> str | None:
        if os.geteuid() == 0:
            return ""
        return shutil.which(self.privileged_launcher)

    def available(self) -> bool:
        return self._resolved_helper() is not None and self._resolved_launcher() is not None

    def _command(self, *arguments: str) -> list[str]:
        helper = self._resolved_helper()
        if not helper:
            raise BackendError(
                "COSMIC DRM backend unavailable: cosmic-nightlight-helper "
                "was not found or is not executable"
            )

        launcher = self._resolved_launcher()
        if launcher is None:
            raise BackendError(
                f"COSMIC DRM backend requires {self.privileged_launcher!r} "
                "or an already-privileged execution context"
            )

        if launcher:
            return [launcher, helper, *arguments]
        return [helper, *arguments]

    def _run(self, *arguments: str) -> None:
        result = subprocess.run(
            self._command(*arguments),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise BackendError(detail or f"COSMIC helper exited with status {result.returncode}")

    def apply(self, temperature: int, brightness: float) -> None:
        self._run("--temp", str(int(temperature)), "--brightness", f"{brightness:.3f}")

    def off(self) -> None:
        self._run("--off")
