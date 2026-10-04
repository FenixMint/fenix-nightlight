from __future__ import annotations

from abc import ABC, abstractmethod


class BackendError(RuntimeError):
    pass


class Backend(ABC):
    name = "unknown"

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, temperature: int, brightness: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def off(self) -> None:
        raise NotImplementedError
