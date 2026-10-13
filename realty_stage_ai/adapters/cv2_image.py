"""Image adapter — decode/encode, mask feathering, luma, warm shift."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


class Cv2ImageAdapter:
    def __init__(self, max_pixels: int = 80_000_000) -> None:
        self._max_pixels = max_pixels

    def load_rgb(self, path: str) -> np.ndarray:
        with Image.open(path) as img:
            w, h = img.size
            if w * h > self._max_pixels:
                raise ValueError(f"image too large: {w}x{h} > {self._max_pixels} px")
            return np.asarray(img.convert("RGB"), dtype=np.uint8)

    def feather_mask(self, mask: np.ndarray, radius: int = 12) -> np.ndarray:
        img = Image.fromarray(mask, mode="L").filter(ImageFilter.GaussianBlur(radius=radius))
        return np.asarray(img, dtype=np.uint8)

    def to_luma(self, rgb: np.ndarray) -> np.ndarray:
        return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).astype(np.float32)

    def warm_shift(self, rgb: np.ndarray, kelvin_delta: int, luma: np.ndarray) -> np.ndarray:
        """Shift color temperature without changing luminance."""
        t = np.clip(kelvin_delta / 2000.0, -1.0, 1.0)
        r_gain = 1.0 + 0.15 * t
        b_gain = 1.0 - 0.15 * t
        shifted = rgb.astype(np.float32).copy()
        shifted[..., 0] *= r_gain
        shifted[..., 2] *= b_gain
        new_luma = self.to_luma(np.clip(shifted, 0, 255))
        scale = np.where(new_luma > 1e-3, luma / np.maximum(new_luma, 1e-3), 1.0)
        return np.clip(shifted * scale[..., None], 0, 255).astype(np.uint8)