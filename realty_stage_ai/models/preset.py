"""Preset schema — the TOML contract for a staging style."""
from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class RelightProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    ambient: float = Field(ge=0.0, le=2.0, default=0.85)
    key_strength: float = Field(ge=0.0, le=2.0, default=0.35)
    depth_gamma: float = Field(gt=0.0, le=4.0, default=0.9)
    kelvin_delta: int = Field(ge=-2000, le=2000, default=150)


class FurnitureSprite(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    anchor: tuple[int, int]
    image: np.ndarray
    alpha: np.ndarray


class StagingPreset(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    room: str = "living"
    erase_existing: bool = True
    mask_feather_px: int = Field(ge=1, le=24, default=12)
    jpeg_quality: int = Field(ge=70, le=100, default=92)
    relight: RelightProfile = RelightProfile()
    furniture_sprites: list[FurnitureSprite] = []

    def build_erase_mask(self, shape: tuple[int, int], depth: np.ndarray) -> np.ndarray:
        """Erase foreground clutter: anything in the near field above the floor line."""
        h, w = shape
        yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
        floor_bias = np.clip(1.0 - yy * 1.4, 0.0, 1.0)
        mask = ((depth > 0.55) & (floor_bias > 0.15)).astype(np.uint8) * 255
        return mask