"""Top-level staging service. Composes depth + inpaint + relight + preset."""
from __future__ import annotations

import time

import numpy as np

from realty_stage_ai.models.preset import StagingPreset
from realty_stage_ai.models.staging_request import StagingRequest
from realty_stage_ai.models.staging_result import StagingResult
from realty_stage_ai.services.depth_service import DepthService
from realty_stage_ai.services.inpaint_service import InpaintService
from realty_stage_ai.services.preset_service import PresetService
from realty_stage_ai.services.relight_service import RelightService


class StagingService:
    def __init__(
        self,
        depth: DepthService,
        inpaint: InpaintService,
        relight: RelightService,
        presets: PresetService,
    ) -> None:
        self._depth = depth
        self._inpaint = inpaint
        self._relight = relight
        self._presets = presets

    def stage(self, request: StagingRequest) -> StagingResult:
        t0 = time.perf_counter()
        preset: StagingPreset = self._presets.get(request.preset)
        rgb = request.decode_source()
        depth = self._depth.estimate(rgb)

        # 1) Erase existing furniture if the preset asks for a full restyle.
        working = rgb
        if preset.erase_existing:
            mask = preset.build_erase_mask(rgb.shape[:2], depth)
            working = self._inpaint.erase(rgb, mask, feather_px=preset.mask_feather_px)

        # 2) Composite the preset's furniture sprites using depth-sorted placement.
        if preset.furniture_sprites:
            working = _composite_sprites(working, depth, preset)

        # 3) Relight.
        relit = self._relight.apply(working, depth, preset.relight)

        out_path = request.output_dir / f"{request.source.stem}.{request.preset}.stage.jpg"
        StagingResult.write_jpeg(out_path, relit, quality=preset.jpeg_quality)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        return StagingResult(output_path=out_path, elapsed_ms=elapsed_ms, preset=request.preset)


def _composite_sprites(rgb: np.ndarray, depth: np.ndarray, preset: StagingPreset) -> np.ndarray:
    """Naive painter's-algorithm composite. Sprite placement is preset-authored."""
    canvas = rgb.copy()
    for sprite in preset.furniture_sprites:
        y0, x0 = sprite.anchor
        sh, sw = sprite.image.shape[:2]
        y1, x1 = min(y0 + sh, canvas.shape[0]), min(x0 + sw, canvas.shape[1])
        if y0 >= canvas.shape[0] or x0 >= canvas.shape[1]:
            continue
        patch = canvas[y0:y1, x0:x1].astype(np.float32)
        alpha = sprite.alpha[: y1 - y0, : x1 - x0, None].astype(np.float32) / 255.0
        blended = patch * (1 - alpha) + sprite.image[: y1 - y0, : x1 - x0].astype(np.float32) * alpha
        canvas[y0:y1, x0:x1] = np.clip(blended, 0, 255).astype(np.uint8)
    return canvas