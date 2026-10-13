"""Batch handler — fans out single-photo staging across a directory."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from loguru import logger

from realty_stage_ai.models.staging_request import StagingRequest
from realty_stage_ai.models.staging_result import StagingResult
from realty_stage_ai.services.staging_service import StagingService

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def iter_listing_photos(folder: Path) -> Iterable[Path]:
    for candidate in sorted(folder.iterdir()):
        if candidate.is_file() and candidate.suffix.lower() in _IMAGE_SUFFIXES:
            yield candidate


def handle_batch(
    folder: Path,
    preset: str,
    output_dir: Path,
    service: StagingService,
    seed: int = 6767,
) -> list[StagingResult]:
    results: list[StagingResult] = []
    for photo in iter_listing_photos(folder):
        request = StagingRequest(source=photo, preset=preset, room="auto", output_dir=output_dir, seed=seed)
        try:
            results.append(service.stage(request))
        except Exception as exc:  # noqa: BLE001 — batch must not die on one bad photo
            logger.warning("skip {}: {}", photo.name, exc)
    return results