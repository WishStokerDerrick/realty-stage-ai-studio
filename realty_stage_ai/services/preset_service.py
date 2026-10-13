"""Loads staging presets (room style, furniture palette, relight profile)."""
from __future__ import annotations

import tomllib
from pathlib import Path

from realty_stage_ai.models.preset import StagingPreset


class PresetService:
    def __init__(self, preset_dir: Path) -> None:
        self._dir = preset_dir
        self._cache: dict[str, StagingPreset] = {}

    def get(self, name: str) -> StagingPreset:
        if name in self._cache:
            return self._cache[name]
        path = self._dir / f"{name}.toml"
        if not path.exists():
            raise FileNotFoundError(f"preset '{name}' not found at {path}")
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        preset = StagingPreset.model_validate(raw)
        self._cache[name] = preset
        return preset

    def list_names(self) -> list[str]:
        return sorted(p.stem for p in self._dir.glob("*.toml"))