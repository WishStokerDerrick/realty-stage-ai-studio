"""Result model — where the staged render landed and how long it took."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from pydantic import BaseModel, ConfigDict


class StagingResult(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    output_path: Path
    elapsed_ms: int
    preset: str

    @staticmethod
    def write_jpeg(path: Path, rgb: np.ndarray, quality: int = 92) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgb, mode="RGB").save(path, format="JPEG", quality=quality, subsampling=0, optimize=True)