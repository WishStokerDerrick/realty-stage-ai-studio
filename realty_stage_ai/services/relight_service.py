"""Relight pass — harmonizes color temperature and shadow direction with the preset."""
from __future__ import annotations

import numpy as np

from realty_stage_ai.adapters.cv2_image import Cv2ImageAdapter
from realty_stage_ai.models.preset import RelightProfile


class RelightService:
    def __init__(self, image: Cv2ImageAdapter) -> None:
        self._image = image

    def apply(self, rgb: np.ndarray, depth: np.ndarray, profile: RelightProfile) -> np.ndarray:
        """Simple albedo-preserving relight: modulate luminance by depth-based falloff."""
        lum = self._image.to_luma(rgb)
        falloff = np.power(np.clip(depth, 0.0, 1.0), profile.depth_gamma)
        gain = profile.ambient + profile.key_strength * (1.0 - falloff)
        relit = np.clip(rgb.astype(np.float32) * gain[..., None], 0, 255).astype(np.uint8)
        return self._image.warm_shift(relit, kelvin_delta=profile.kelvin_delta, luma=lum)