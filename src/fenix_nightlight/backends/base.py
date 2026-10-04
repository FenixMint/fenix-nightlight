from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class BackendError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackendCapabilities:
    smooth_transitions: bool = True
    requires_privilege: bool = False
    may_flicker: bool = False


class Backend(ABC):
    name = "unknown"
    aliases: tuple[str, ...] = ()
    capabilities = BackendCapabilities()

    def matches(self, requested: str) -> bool:
        return requested == self.name or requested in self.aliases

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self, temperature: int, brightness: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def off(self) -> None:
        raise NotImplementedError
