from __future__ import annotations

from .base import Backend, BackendError
from .cosmic import CosmicBackend
from ..config import Settings


def get_backend(settings: Settings) -> Backend:
    requested = settings.backend.lower().strip()
    candidates = [CosmicBackend(settings.cosmic_helper)]

    if requested == "auto":
        for backend in candidates:
            if backend.available():
                return backend
        raise BackendError("no supported color-temperature backend is available")

    for backend in candidates:
        if backend.name == requested:
            if not backend.available():
                raise BackendError(f"requested backend '{requested}' is not available")
            return backend

    raise BackendError(f"unknown backend: {settings.backend}")


__all__ = ["Backend", "BackendError", "get_backend"]
