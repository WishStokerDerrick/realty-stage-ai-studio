"""Filesystem artifact store — confines writes to a configured output root."""
from __future__ import annotations

from pathlib import Path


class FsArtifactStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def resolve(self, requested: Path) -> Path:
        target = (self._root / requested).resolve() if not requested.is_absolute() else requested.resolve()
        if self._root not in target.parents and target != self._root:
            raise PermissionError(f"refusing to write outside output_root: {target}")
        return target

    def write_bytes(self, requested: Path, payload: bytes) -> Path:
        target = self.resolve(requested)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target