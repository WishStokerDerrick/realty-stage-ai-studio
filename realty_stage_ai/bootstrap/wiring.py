"""Composition root. Builds the service container from settings."""
from __future__ import annotations

from dataclasses import dataclass

from realty_stage_ai.adapters.cv2_image import Cv2ImageAdapter
from realty_stage_ai.adapters.fs_store import FsArtifactStore
from realty_stage_ai.adapters.onnx_runtime import OnnxRuntimeAdapter
from realty_stage_ai.config.settings import Settings
from realty_stage_ai.services.depth_service import DepthService
from realty_stage_ai.services.inpaint_service import InpaintService
from realty_stage_ai.services.model_registry import ModelRegistry
from realty_stage_ai.services.preset_service import PresetService
from realty_stage_ai.services.relight_service import RelightService
from realty_stage_ai.services.staging_service import StagingService


@dataclass(frozen=True, slots=True)
class Container:
    image: Cv2ImageAdapter
    store: FsArtifactStore
    registry: ModelRegistry
    presets: PresetService
    depth: DepthService
    inpaint: InpaintService
    relight: RelightService
    staging: StagingService


def build_container(settings: Settings) -> Container:
    image = Cv2ImageAdapter(max_pixels=settings.max_pixels)
    store = FsArtifactStore(root=settings.output_root)
    runtime = OnnxRuntimeAdapter(providers=settings.onnx_providers)
    registry = ModelRegistry(runtime=runtime, weights_lock=settings.weights_lock)
    presets = PresetService(preset_dir=settings.preset_dir)
    depth = DepthService(registry=registry)
    inpaint = InpaintService(registry=registry, image=image)
    relight = RelightService(image=image)
    staging = StagingService(depth=depth, inpaint=inpaint, relight=relight, presets=presets)
    return Container(
        image=image,
        store=store,
        registry=registry,
        presets=presets,
        depth=depth,
        inpaint=inpaint,
        relight=relight,
        staging=staging,
    )