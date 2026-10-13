"""Loads and caches ONNX models pinned by SHA-256 in weights.lock.toml."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from loguru import logger


class _Runtime(Protocol):
    def load(self, path: Path) -> object: ...


@dataclass(frozen=True, slots=True)
class WeightsLockEntry:
    name: str
    sha256: str
    filename: str


class ModelRegistry:
    """Resolves model names to loaded sessions. Verifies hash on first load."""

    def __init__(self, runtime: _Runtime, weights_lock: dict[str, WeightsLockEntry]) -> None:
        self._runtime = runtime
        self._lock = weights_lock
        self._cache: dict[str, object] = {}

    def get(self, name: str) -> object:
        if name in self._cache:
            return self._cache[name]
        entry = self._lock.get(name)
        if entry is None:
            raise KeyError(f"model '{name}' is not in weights.lock.toml")
        path = Path(entry.filename)
        digest = _sha256(path)
        if digest != entry.sha256:
            raise RuntimeError(f"weights hash mismatch for {name}: {digest} != {entry.sha256}")
        logger.info("loading model {} from {}", name, path)
        session = self._runtime.load(path)
        self._cache[name] = session
        return session


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()