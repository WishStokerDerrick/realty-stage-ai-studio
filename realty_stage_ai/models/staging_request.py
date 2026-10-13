"""Domain model for a single-photo staging request."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from pydantic import BaseModel, ConfigDict, field_validator


class StagingRequest(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    source: Path
    preset: str
    room: str = "auto"
    output_dir: Path
    seed: int = 6767

    @field_validator("source")
    @classmethod
    def _source_must_be_image(cls, value: Path) -> Path:
        if value.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
            raise ValueError(f"unsupported image suffix: {value.suffix}")
        return value

    def validate_for_disk(self) -> None:
        if not self.source.exists():
            raise FileNotFoundError(self.source)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def decode_source(self) -> np.ndarray:
        from PIL import Image

        with Image.open(self.source) as img:
            return np.asarray(img.convert("RGB"), dtype=np.uint8)