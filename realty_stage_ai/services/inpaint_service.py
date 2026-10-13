"""Inpainting service — fills masked regions (removed furniture, added pieces)."""
from __future__ import annotations

import numpy as np

from realty_stage_ai.adapters.cv2_image import Cv2ImageAdapter
from realty_stage_ai.services.model_registry import ModelRegistry


class InpaintService:
    def __init__(self, registry: ModelRegistry, image: Cv2ImageAdapter, model_name: str = "lama_inpaint") -> None:
        self._registry = registry
        self._image = image
        self._model_name = model_name

    def erase(self, rgb: np.ndarray, mask: np.ndarray, feather_px: int = 12) -> np.ndarray:
        """Erase masked content and inpaint. Mask is HxW uint8 {0,255}."""
        if mask.shape[:2] != rgb.shape[:2]:
            raise ValueError(f"mask shape {mask.shape} != image shape {rgb.shape}")
        feathered = self._image.feather_mask(mask, radius=min(max(feather_px, 1), 24))
        session = self._registry.get(self._model_name)
        out = session.run(  # type: ignore[attr-defined]
            None,
            {"image": _nchw(rgb), "mask": _nchw_mask(feathered)},
        )[0]
        return np.clip(np.transpose(np.asarray(out).squeeze(0), (1, 2, 0)) * 255.0, 0, 255).astype(np.uint8)


def _nchw(rgb: np.ndarray) -> np.ndarray:
    return np.transpose(rgb.astype(np.float32) / 255.0, (2, 0, 1))[None, ...]


def _nchw_mask(mask: np.ndarray) -> np.ndarray:
    return (mask.astype(np.float32) / 255.0)[None, None, ...]