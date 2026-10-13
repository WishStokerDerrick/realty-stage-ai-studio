"""Monocular depth estimation. Produces a normalized inverse-depth map."""
from __future__ import annotations

import numpy as np

from realty_stage_ai.services.model_registry import ModelRegistry


class DepthService:
    """Wraps the depth model. Input: HxWx3 uint8 RGB. Output: HxW float32 in [0,1]."""

    def __init__(self, registry: ModelRegistry, model_name: str = "depth_anything_v2_small") -> None:
        self._registry = registry
        self._model_name = model_name

    def estimate(self, rgb: np.ndarray) -> np.ndarray:
        if rgb.ndim != 3 or rgb.shape[2] != 3:
            raise ValueError(f"expected HxWx3 RGB, got {rgb.shape}")
        session = self._registry.get(self._model_name)
        # Session is duck-typed; concrete impl lives in adapters/onnx_runtime.py.
        raw = session.run(None, {"image": _to_nchw(rgb)})[0]  # type: ignore[attr-defined]
        depth = np.asarray(raw, dtype=np.float32).squeeze()
        lo, hi = float(depth.min()), float(depth.max())
        if hi - lo < 1e-6:
            return np.zeros_like(depth)
        return (depth - lo) / (hi - lo)


def _to_nchw(rgb: np.ndarray) -> np.ndarray:
    chw = np.transpose(rgb.astype(np.float32) / 255.0, (2, 0, 1))
    return chw[None, ...]