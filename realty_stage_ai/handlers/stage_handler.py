"""Handler for a single-photo staging request. No business logic here."""
from __future__ import annotations

from realty_stage_ai.models.staging_request import StagingRequest
from realty_stage_ai.models.staging_result import StagingResult
from realty_stage_ai.services.staging_service import StagingService


def handle_stage(request: StagingRequest, service: StagingService) -> StagingResult:
    """Validate + delegate. Any exception from the service propagates."""
    request.validate_for_disk()
    return service.stage(request)